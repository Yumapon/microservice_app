/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import {
  Chart as ChartJS,
  LineElement,
  BarElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'
import annotationPlugin from 'chartjs-plugin-annotation'
import { Chart } from 'react-chartjs-2'

ChartJS.register(LineElement, BarElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend, annotationPlugin)

type Props = {
  paymentPeriod: number
  monthlyPremium?: number
}

export const SurrenderValueChart = ({ paymentPeriod, monthlyPremium = 20000 }: Props) => {
  const years = Array.from({ length: paymentPeriod + 6 }, (_, i) => i + 1)

  const surrenderRateList = years.map((year) => {
    if (year < 5) return 0.7 + 0.1 * (year - 1)
    if (year <= paymentPeriod) return 1.0
    const maxRate = 1.3
    const step = (maxRate - 1.0) / 5
    return Math.min(1.0 + step * (year - paymentPeriod), maxRate)
  })

  const paidList = years.map((year) =>
    year <= paymentPeriod ? monthlyPremium * 12 * year : monthlyPremium * 12 * paymentPeriod
  )

  const refundAmountList = years.map((_, i) => Math.round(paidList[i] * surrenderRateList[i]))

  const firstOverIndex = surrenderRateList.findIndex((r) => r > 1.0)

  const data = {
    labels: years.map((y) => `${y}年目`),
    datasets: [
      {
        type: 'bar' as const,
        label: '返戻金額（円）',
        data: refundAmountList,
        backgroundColor: '#cbd5e1',
        yAxisID: 'y1',
      },
      {
        type: 'line' as const,
        label: '返戻率（%）',
        data: surrenderRateList.map((r) => +(r * 100).toFixed(1)),
        borderColor: '#2563eb',
        backgroundColor: '#3b82f6',
        yAxisID: 'y',
        fill: false,
        tension: 0.3,
        pointRadius: 4,
        pointBackgroundColor: surrenderRateList.map((r) => (r >= 1.0 ? '#22c55e' : '#2563eb')),
      },
    ],
  }

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      y: {
        type: 'linear' as const,
        position: 'left' as const,
        beginAtZero: true,
        ticks: {
          callback: function (tickValue: string | number) {
            return `${tickValue}%`
          },
        },
        title: {
          display: true,
          text: '返戻率',
        },
        max: 140,
      },
      y1: {
        type: 'linear' as const,
        position: 'right' as const,
        beginAtZero: true,
        grid: {
          drawOnChartArea: false,
        },
        title: {
          display: true,
          text: '返戻金額（円）',
        },
      },
    },
  }

  return (
    <div css={wrapper}>
      <h4 css={title}>年ごとの返戻率・返戻金額 推移</h4>
      {firstOverIndex >= 0 && (
        <p css={infoText}>
          <strong>{years[firstOverIndex]}年目</strong>で返戻率が100%を超えます。
        </p>
      )}
      <div css={chartBox}>
        <Chart type='bar' data={data} options={options} />
      </div>
    </div>
  )
}

// ----------------------
// Styles
// ----------------------
const wrapper = css`
  margin-top: 2.5rem;
`

const title = css`
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: #0f172a;
`

const infoText = css`
  font-size: 0.95rem;
  color: #334155;
  margin-bottom: 1rem;
`

const chartBox = css`
  width: 100%;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
`