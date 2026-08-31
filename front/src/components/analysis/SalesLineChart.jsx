// recharts 사용: 사용자 확인 하에 package.json에 설치됨 (§11-4 참고)
// 실측 매출(actual) / AI 예측 매출(predicted) / 목표 매출(target)을 하나의 라인 차트로 표시
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function SalesLineChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#DCE7E4" />
        <XAxis dataKey="quarter" tick={{ fontSize: 12, fill: "#82918E" }} />
        <YAxis tick={{ fontSize: 12, fill: "#82918E" }} />
        <Tooltip />
        <Legend />
        <Line
          type="monotone"
          dataKey="actual"
          name="실측 매출"
          stroke="#1F706A"
          strokeWidth={3}
          connectNulls
          dot={{ r: 4 }}
        />
        <Line
          type="monotone"
          dataKey="predicted"
          name="AI 예측 매출"
          stroke="#1F706A"
          strokeWidth={3}
          strokeDasharray="6 4"
          connectNulls
          dot={{ r: 4 }}
        />
        <Line
          type="monotone"
          dataKey="target"
          name="목표 매출"
          stroke="#44BB00"
          strokeWidth={2}
          strokeDasharray="4 4"
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export default SalesLineChart;
