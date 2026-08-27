import Card from "./Card.jsx";

function StatTile({ label, value, hint }) {
  return (
    <Card className="stat-tile">
      <div className="stat-tile__label">{label}</div>
      <div className="stat-tile__value">{value ?? "-"}</div>
      <div className="stat-tile__hint">{hint}</div>
    </Card>
  );
}

export default StatTile;
