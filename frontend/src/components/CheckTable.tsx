interface CheckItem {
  check: string;
  importance: string;
  output: string;
  notes: string;
}

interface CheckTableProps {
  items: CheckItem[];
}

const CheckTable = ({ items }: CheckTableProps) => {
  return (
    <div className="overflow-x-auto rounded-xl border border-border">
      <table className="table-portal">
        <thead>
          <tr>
            <th>סעיף בדיקה</th>
            <th>למה זה חשוב</th>
            <th>פלט אפשרי</th>
            <th>הערות</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, index) => (
            <tr key={index}>
              <td className="font-medium">{item.check}</td>
              <td className="text-muted-foreground">{item.importance}</td>
              <td>{item.output}</td>
              <td className="text-muted-foreground">{item.notes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CheckTable;
