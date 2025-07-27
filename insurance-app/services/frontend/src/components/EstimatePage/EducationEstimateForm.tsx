/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const EducationEstimateForm = () => {
  const [form, setForm] = useState({
    childBirthDate: '',
    parentName: '',
    parentBirthDate: '',
    parentGender: '',
    paymentAmount: '',
    paymentMethod: '',
  })

  const [result, setResult] = useState<null | {
    totalPaid: number
    expectedReturn: number
    returnRate: number
    bonusSchedule: { age: number; amount: number }[]
  }>(null)

  const navigate = useNavigate()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const payment = parseInt(form.paymentAmount)
    if (!payment || isNaN(payment)) return

    const years = 18
    const totalPaid =
      form.paymentMethod === 'monthly'
        ? payment * 12 * years
        : form.paymentMethod === 'yearly'
        ? payment * years
        : payment

    const expectedReturn = Math.round(totalPaid * 1.25)
    const returnRate = expectedReturn / totalPaid

    const bonusSchedule = [
      { age: 15, amount: 200000 },
      { age: 18, amount: 300000 },
      { age: 22, amount: 500000 },
    ]

    setResult({
      totalPaid,
      expectedReturn,
      returnRate,
      bonusSchedule,
    })
  }

  const handleReset = () => {
    setResult(null)
  }

  const handleApply = () => {
    navigate('/apply/education')
  }

  return (
    <div css={formWrapper}>
      {!result && (
        <form onSubmit={handleSubmit} css={formStyle}>
          <h2 css={sectionTitle}>学資保険 見積もりフォーム</h2>

          <label>
            子どもの生年月日
            <input type="date" name="childBirthDate" value={form.childBirthDate} onChange={handleChange} required />
          </label>

          <label>
            契約者氏名
            <input type="text" name="parentName" value={form.parentName} onChange={handleChange} required />
          </label>

          <label>
            契約者の生年月日
            <input type="date" name="parentBirthDate" value={form.parentBirthDate} onChange={handleChange} required />
          </label>

          <label>
            契約者の性別
            <select name="parentGender" value={form.parentGender} onChange={handleChange} required>
              <option value="">選択してください</option>
              <option value="male">男性</option>
              <option value="female">女性</option>
            </select>
          </label>

          <label>
            保険料（月額 or 年額）
            <input
              type="number"
              name="paymentAmount"
              value={form.paymentAmount}
              onChange={handleChange}
              required
              placeholder="例）10000"
              min={1000}
            />
          </label>

          <label>
            払込方法
            <select name="paymentMethod" value={form.paymentMethod} onChange={handleChange} required>
              <option value="">選択してください</option>
              <option value="monthly">月払</option>
              <option value="yearly">年払</option>
              <option value="lump">全期前納</option>
            </select>
          </label>

          <button type="submit">見積もりを計算する</button>
        </form>
      )}

      {result && (
        <div css={resultBox}>
          <h3>見積もり結果</h3>

          <div css={amountRow}>
            <div css={amountItem}>
              <p className="label">払込総額</p>
              <p className="value">{result.totalPaid.toLocaleString()}円</p>
            </div>
            <div css={amountItem}>
              <p className="label">想定受取額</p>
              <p className="value">{result.expectedReturn.toLocaleString()}円</p>
            </div>
          </div>

          <p css={returnRate}>
            返戻率：<span>{(result.returnRate * 100).toFixed(1)}%</span>
          </p>

          <div css={bonusTableBox}>
            <h4>祝金の受取スケジュール</h4>
            <table css={bonusTable}>
              <thead>
                <tr>
                  <th>年齢</th>
                  <th>受取金額</th>
                </tr>
              </thead>
              <tbody>
                {result.bonusSchedule.map((bonus, index) => (
                  <tr key={index}>
                    <td>{bonus.age}歳</td>
                    <td>{bonus.amount.toLocaleString()}円</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div css={actionButtons}>
            <button onClick={handleApply}>この内容で申し込む</button>
            <button onClick={handleReset} className="secondary">条件を変えて見積もりする</button>
          </div>
        </div>
      )}
    </div>
  )
}

export default EducationEstimateForm

const formWrapper = css`
  max-width: 560px;
  margin: 2rem auto;
`

const formStyle = css`
  display: flex;
  flex-direction: column;
  gap: 1.25rem;

  label {
    font-weight: 600;
    font-size: 0.95rem;
    display: flex;
    flex-direction: column;
  }

  input,
  select {
    margin-top: 0.4rem;
    padding: 0.6rem;
    font-size: 1rem;
    border-radius: 6px;
    border: 1px solid #ccc;
  }

  button {
    background-color: #3b82f6;
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 6px;
    padding: 0.75rem;
    cursor: pointer;

    &:hover {
      background-color: #2563eb;
    }
  }
`

const sectionTitle = css`
  font-size: 1.3rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 1rem;
`

const resultBox = css`
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  padding: 2rem;
  border-radius: 12px;
`

const amountRow = css`
  display: flex;
  justify-content: space-around;
  margin-bottom: 1rem;
`

const amountItem = css`
  .label {
    font-size: 0.9rem;
    text-align: center;
    color: #4b5563;
  }
  .value {
    font-size: 1.3rem;
    font-weight: bold;
    color: #065f46;
    text-align: center;
  }
`

const returnRate = css`
  text-align: center;
  margin: 1rem 0;
  font-size: 1rem;

  span {
    font-size: 1.5rem;
    font-weight: bold;
    color: #16a34a;
  }
`

const bonusTableBox = css`
  margin-top: 1.5rem;
`

const bonusTable = css`
  width: 100%;
  border-collapse: collapse;

  th,
  td {
    padding: 0.6rem;
    border: 1px solid #ccc;
    text-align: center;
  }

  th {
    background-color: #dcfce7;
  }

  td {
    background-color: #ffffff;
  }
`

const actionButtons = css`
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;

  button {
    padding: 0.75rem 1.5rem;
    font-weight: bold;
    border-radius: 9999px;
    border: none;
    cursor: pointer;

    &:first-of-type {
      background-color: #10b981;
      color: white;

      &:hover {
        background-color: #059669;
      }
    }

    &.secondary {
      background-color: #e5e7eb;
      color: #374151;

      &:hover {
        background-color: #d1d5db;
      }
    }
  }
`