"""
Apify client wrapper for data fetching.

This module provides a simplified interface to the Apify API for running
web scraping actors and retrieving results.
"""

import os
import asyncio
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

import httpx

from .constants import APIFY_ACTORS

logger = logging.getLogger(__name__)

# Apify API base URL
APIFY_API_BASE = "https://api.apify.com/v2"


class ApifyError(Exception):
    """Exception raised when Apify operations fail."""
    pass


class ApifyClient:
    """
    Async client for Apify API.

    Usage:
        async with ApifyClient() as client:
            result = await client.run_actor("K9WppTziYC3n2vxTu", input_data={})
    """

    def __init__(
        self,
        api_token: Optional[str] = None,
        timeout: int = 300,
        max_retries: int = 3,
    ):
        """
        Initialize Apify client.

        Args:
            api_token: Apify API token. If not provided, reads from APIFY_API_TOKEN env var.
            timeout: Maximum time to wait for actor run (seconds).
            max_retries: Number of retries for failed requests.
        """
        self.api_token = api_token or os.environ.get("APIFY_API_TOKEN")
        if not self.api_token:
            raise ApifyError("APIFY_API_TOKEN not set")

        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_token}"},
            timeout=httpx.Timeout(30.0),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise ApifyError("Client not initialized. Use 'async with ApifyClient()' context.")
        return self._client

    async def run_actor(
        self,
        actor_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        wait_for_finish: bool = True,
    ) -> Dict[str, Any]:
        """
        Run an Apify actor and optionally wait for completion.

        Args:
            actor_id: The actor ID to run.
            input_data: Input data for the actor.
            wait_for_finish: Whether to wait for the actor to complete.

        Returns:
            Actor run result with dataset items.
        """
        logger.info(f"Starting Apify actor: {actor_id}")

        # Start the actor run
        url = f"{APIFY_API_BASE}/acts/{actor_id}/runs"
        response = await self.client.post(
            url,
            json=input_data or {},
            params={"waitForFinish" if wait_for_finish else "": str(self.timeout)},
        )

        if response.status_code != 201:
            raise ApifyError(f"Failed to start actor: {response.text}")

        run_data = response.json()["data"]
        run_id = run_data["id"]
        logger.info(f"Actor run started: {run_id}")

        if wait_for_finish:
            # Wait for completion if requested
            run_data = await self._wait_for_run(run_id)

        return run_data

    async def _wait_for_run(self, run_id: str) -> Dict[str, Any]:
        """Wait for an actor run to complete."""
        url = f"{APIFY_API_BASE}/actor-runs/{run_id}"
        start_time = asyncio.get_event_loop().time()

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > self.timeout:
                raise ApifyError(f"Actor run timed out after {self.timeout} seconds")

            response = await self.client.get(url)
            if response.status_code != 200:
                raise ApifyError(f"Failed to get run status: {response.text}")

            run_data = response.json()["data"]
            status = run_data.get("status")

            if status == "SUCCEEDED":
                logger.info(f"Actor run completed: {run_id}")
                return run_data
            elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
                raise ApifyError(f"Actor run failed with status: {status}")

            # Still running, wait and check again
            await asyncio.sleep(5)

    async def get_dataset_items(
        self,
        dataset_id: str,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get items from an Apify dataset.

        Args:
            dataset_id: The dataset ID.
            limit: Maximum number of items to retrieve.
            offset: Number of items to skip.

        Returns:
            List of dataset items.
        """
        url = f"{APIFY_API_BASE}/datasets/{dataset_id}/items"
        params = {"offset": offset}
        if limit:
            params["limit"] = limit

        response = await self.client.get(url, params=params)
        if response.status_code != 200:
            raise ApifyError(f"Failed to get dataset items: {response.text}")

        return response.json()

    async def get_key_value_store_record(
        self,
        store_id: str,
        key: str,
    ) -> Any:
        """
        Get a record from an Apify key-value store.

        Args:
            store_id: The key-value store ID.
            key: The record key.

        Returns:
            The record value.
        """
        url = f"{APIFY_API_BASE}/key-value-stores/{store_id}/records/{key}"
        response = await self.client.get(url)

        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise ApifyError(f"Failed to get KV record: {response.text}")

        # Return raw content if not JSON
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        return response.content

    async def download_file(
        self,
        store_id: str,
        key: str,
        output_path: Path,
    ) -> Path:
        """
        Download a file from an Apify key-value store.

        Args:
            store_id: The key-value store ID.
            key: The file key.
            output_path: Path to save the file.

        Returns:
            Path to the downloaded file.
        """
        content = await self.get_key_value_store_record(store_id, key)
        if content is None:
            raise ApifyError(f"File not found: {key}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(content if isinstance(content, bytes) else content.encode())

        logger.info(f"Downloaded file: {output_path}")
        return output_path


async def fetch_funds_list(output_path: Optional[Path] = None) -> Path:
    """
    Fetch the mutual funds list from TASE Maya via Apify.

    Args:
        output_path: Path to save the file. If not provided, saves to temp directory.

    Returns:
        Path to the downloaded file.
    """
    if output_path is None:
        output_path = Path("temp") / "Mutual_Funds_List.xlsx"

    async with ApifyClient() as client:
        run_data = await client.run_actor(
            APIFY_ACTORS["funds_list"],
            input_data={},
        )

        kv_store_id = run_data.get("defaultKeyValueStoreId")
        if not kv_store_id:
            raise ApifyError("No key-value store in run result")

        return await client.download_file(
            kv_store_id,
            "Mutual_Funds_List.xlsx",
            output_path,
        )


async def fetch_manager_report(
    manager_id: str,
    event_id: int,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Fetch a manager's report from TASE Maya via Apify.

    Args:
        manager_id: The manager's item ID.
        event_id: The TASE Maya event ID.
        output_path: Path to save the file.

    Returns:
        Path to the downloaded file.
    """
    if output_path is None:
        output_path = Path("temp") / f"report_{manager_id}.csv"

    async with ApifyClient() as client:
        run_data = await client.run_actor(
            APIFY_ACTORS["reports"],
            input_data={
                "itemId": manager_id,
                "eventId": event_id,
            },
        )

        dataset_id = run_data.get("defaultDatasetId")
        if not dataset_id:
            raise ApifyError("No dataset in run result")

        items = await client.get_dataset_items(dataset_id)
        if not items:
            raise ApifyError("No items in dataset")

        # Save as CSV
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # Implementation depends on the actual data structure
        # This is a placeholder
        import json
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

        return output_path
