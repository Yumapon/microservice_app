/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { FaCreditCard } from 'react-icons/fa'
import dayjs from 'dayjs'

const mockPaymentInfo = {
  paymentMethod: 'クレジットカード',
  nextPaymentDate: '2025-08-01',
  lastStatus: 'pending', // success, failed, pending
  totalPaid: 240000,
}

const mockHistory = [
  { date: '2025-07-01', amount: 20000, status: 'pending' },
  { date: '2025-06-01', amount: 20000, status: 'success' },
  { date: '2025-05-01', amount: 20000, status: 'success' },
  { date: '2025-04-01', amount: 20000, status: 'failed' },
]

export const PaymentHistory = () => {
  const theme = useTheme()

  return (
    <section css={wrapperStyle}>
      <h2 css={titleStyle(theme)}>
        <FaCreditCard style={{ marginRight: '0.5rem' }} />
        支払い情報
      </h2>

      <div css={summaryBox(theme)}>
        <div>
          <p><strong>支払い方法：</strong>{mockPaymentInfo.paymentMethod}</p>
          <p><strong>次回支払い予定日：</strong>{dayjs(mockPaymentInfo.nextPaymentDate).format('YYYY年MM月DD日')}</p>
          <p><strong>直近の支払い状況：</strong>
            <span css={statusBadge(mockPaymentInfo.lastStatus)}>
              {mockPaymentInfo.lastStatus === 'success'
                ? '正常'
                : mockPaymentInfo.lastStatus === 'failed'
                ? '失敗'
                : '保留'}
            </span>
          </p>
          <p><strong>これまでの支払総額：</strong>{mockPaymentInfo.totalPaid.toLocaleString()}円</p>
        </div>
      </div>

      <table css={tableStyle}>
        <thead>
          <tr>
            <th>支払日</th>
            <th>金額</th>
            <th>ステータス</th>
          </tr>
        </thead>
        <tbody>
          {mockHistory.map((record, idx) => (
            <tr key={idx}>
              <td>{dayjs(record.date).format('YYYY/MM/DD')}</td>
              <td>{record.amount.toLocaleString()}円</td>
              <td>
                <span css={statusBadge(record.status)}>
                  {record.status === 'success'
                    ? '成功'
                    : record.status === 'failed'
                    ? '失敗'
                    : '保留'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}

// ----------------------------
// Emotion CSS
// ----------------------------

const wrapperStyle = css`
  margin-bottom: 2.5rem;
`

const titleStyle = (theme: any) => css`
  font-size: 1.4rem;
  font-weight: bold;
  color: ${theme.colors.primary};
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
`

const summaryBox = (theme: any) => css`
  background-color: ${theme.colors.tile};
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  line-height: 1.8;

  p {
    font-size: 0.95rem;
  }
`

const tableStyle = css`
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;

  th, td {
    padding: 0.75rem;
    border-bottom: 1px solid #ddd;
    text-align: left;
  }

  th {
    background-color: #f5f5f5;
  }
`

const statusBadge = (status: string) => css`
  display: inline-block;
  padding: 0.3rem 0.7rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.85rem;
  background-color: ${
    status === 'success'
      ? '#4caf50'
      : status === 'failed'
      ? '#f44336'
      : '#ff9800'
  };
  color: white;
`