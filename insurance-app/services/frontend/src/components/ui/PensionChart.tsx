/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

interface PensionChartProps {
  totalPaid: number
  currentValue: number
}

const PensionChart = ({ totalPaid, currentValue }: PensionChartProps) => {
  const data = {
    labels: ['払込総額', '現在の貯蓄額'],
    datasets: [
      {
        label: '金額（円）',
        data: [totalPaid, currentValue],
        backgroundColor: ['#60a5fa', '#34d399'], // 青 / 緑
        borderRadius: 8,
        barThickness: 40,
      },
    ],
  }

  const options = {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context: any) =>
            `${context.dataset.label}: ${context.raw.toLocaleString()}円`,
        },
      },
    },
    scales: {
      x: {
        ticks: {
          callback: (tickValue: string | number) =>
            typeof tickValue === 'number'
              ? `${tickValue.toLocaleString()}円`
              : `${tickValue}円`,
        },
        grid: {
          color: '#eee',
        },
      },
      y: {
        grid: {
          display: false,
        },
      },
    },
  }

  return (
    <div css={chartContainer}>
      <Bar data={data} options={options} />
    </div>
  )
}

export default PensionChart

const chartContainer = css`
  width: 100%;
  height: 200px;
  margin-top: 1rem;
`