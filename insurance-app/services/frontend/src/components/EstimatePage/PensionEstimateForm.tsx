/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { SurrenderValueChart } from '@/components/ui/SurrenderValueChart'

type PensionEstimateInput = {
  birthDate: string
  gender: 'male' | 'female'
  monthlyPremium: number
  paymentPeriod: number
  taxDeduction: boolean
}

export const PensionEstimateForm = () => {
  const [form, setForm] = useState<PensionEstimateInput>({
    birthDate: '',
    gender: 'male',
    monthlyPremium: 10000,
    paymentPeriod: 15,
    taxDeduction: false,
  })

  const [result, setResult] = useState<null | {
    totalPaid: number
    estimatedRate: number
    returnAmount: number
    returnRate: number
    taxDeducted: number
  }>(null)

  const navigate = useNavigate()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : name === 'monthlyPremium' || name === 'paymentPeriod'
        ? Number(value)
        : value,
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const estimatedRate = 0.015
    const totalPaid = form.monthlyPremium * 12 * form.paymentPeriod
    const returnAmount = Math.round(totalPaid * (1 + estimatedRate * form.paymentPeriod))
    const returnRate = returnAmount / totalPaid
    const taxDeducted = form.taxDeduction ? 40000 * form.paymentPeriod : 0

    setResult({
      totalPaid,
      estimatedRate,
      returnAmount,
      returnRate,
      taxDeducted,
    })
  }

  const handleReset = () => {
    setResult(null)
  }

  const handleApply = () => {
    navigate('/apply/pension')
  }

  return (
    <section css={container}>
      <h2 css={title}>個人年金保険の見積もり</h2>

      {!result ? (
        <form onSubmit={handleSubmit} css={formCard}>
          <div css={formRow}>
            <label>生年月日</label>
            <input type="date" name="birthDate" value={form.birthDate} onChange={handleChange} required />
          </div>
          <div css={formRow}>
            <label>性別</label>
            <select name="gender" value={form.gender} onChange={handleChange}>
              <option value="male">男性</option>
              <option value="female">女性</option>
            </select>
          </div>
          <div css={formRow}>
            <label>月額保険料（円）</label>
            <input
              type="number"
              name="monthlyPremium"
              value={form.monthlyPremium}
              onChange={handleChange}
              min={10000}
              max={50000}
              step={1000}
              required
            />
          </div>
          <div css={formRow}>
            <label>払込期間（年）</label>
            <input
              type="number"
              name="paymentPeriod"
              value={form.paymentPeriod}
              onChange={handleChange}
              min={15}
              max={45}
              required
            />
          </div>
          <div css={formRow}>
            <label>税制適格特約</label>
            <input
              type="checkbox"
              name="taxDeduction"
              checked={form.taxDeduction}
              onChange={handleChange}
            />
          </div>
          <p css={noteText}>
            ※ 契約開始日は、申込が受理された翌月の1日からとなります。<br />
            ※ 利率が変動するため、契約開始月は選べません。
          </p>
          <button type="submit" css={submitButton}>見積もる</button>
        </form>
      ) : (
        <div css={resultCard}>
          <h3>見積もり結果</h3>
          <p>払込総額: {result.totalPaid.toLocaleString()}円</p>
          <p>予定利率: {(result.estimatedRate * 100).toFixed(1)}%</p>
          <p>受取総額（想定）: {result.returnAmount.toLocaleString()}円</p>
          <SurrenderValueChart paymentPeriod={form.paymentPeriod} />
          <p css={rateText}>返戻率: <strong>{(result.returnRate * 100).toFixed(1)}%</strong></p>
          {result.taxDeducted > 0 && (
            <p>税制控除額（想定）: {result.taxDeducted.toLocaleString()}円</p>
          )}
          <div css={buttonGroup}>
            <button onClick={handleApply} css={applyButton}>この内容で申し込む</button>
            <button onClick={handleReset} css={resetButton}>条件を変えて見積もりする</button>
          </div>
        </div>
      )}
    </section>
  )
}

// ------------------------
// CSS
// ------------------------
const container = css`
  max-width: 720px;
  margin: 0 auto;
  padding: 2rem 1rem;
`

const title = css`
  font-size: 1.6rem;
  font-weight: bold;
  margin-bottom: 2rem;
  text-align: center;
`

const formCard = css`
  background: #ffffff;
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
`

const formRow = css`
  display: flex;
  flex-direction: column;
  font-size: 0.95rem;
  font-weight: 600;

  label {
    margin-bottom: 0.5rem;
  }

  input,
  select {
    padding: 0.6rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 8px;
  }

  input[type='checkbox'] {
    width: 1.2rem;
    height: 1.2rem;
  }
`

const submitButton = css`
  align-self: center;
  margin-top: 1rem;
  padding: 0.75rem 2rem;
  background-color: #0ea5e9;
  color: #fff;
  font-size: 1rem;
  font-weight: bold;
  border: none;
  border-radius: 9999px;
  cursor: pointer;

  &:hover {
    background-color: #0284c7;
  }
`

const resultCard = css`
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
`

const rateText = css`
  font-size: 1.1rem;
  font-weight: bold;
  color: #1d4ed8;
  margin: 1rem 0;
`

const buttonGroup = css`
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 2rem;
`

const applyButton = css`
  padding: 0.75rem 2rem;
  background-color: #10b981;
  color: white;
  font-weight: bold;
  border: none;
  border-radius: 9999px;
  cursor: pointer;

  &:hover {
    background-color: #059669;
  }
`

const resetButton = css`
  padding: 0.75rem 2rem;
  background-color: #e5e7eb;
  color: #1f2937;
  font-weight: bold;
  border: none;
  border-radius: 9999px;
  cursor: pointer;

  &:hover {
    background-color: #d1d5db;
  }
`

const noteText = css`
  font-size: 0.85rem;
  color: #666;
  margin-top: 1.2rem;
  line-height: 1.6;
`