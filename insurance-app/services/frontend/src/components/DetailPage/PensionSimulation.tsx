/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { useState } from 'react'

export const PensionSimulation = () => {
  const theme = useTheme()

  const [form, setForm] = useState({
    birthDate: '',
    gender: '',
    monthlyPremium: '',
    paymentYears: '10',
    pensionYears: '10',
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('simulate with:', form)
    // 実際の見積処理は後で実装
  }

  return (
    <section css={sectionStyle}>
      <h2 css={titleStyle}>かんたん見積もり</h2>
      <form onSubmit={handleSubmit} css={formStyle}>
        <div css={formRow}>
          <label>生年月日</label>
          <input
            type="date"
            name="birthDate"
            value={form.birthDate}
            onChange={handleChange}
            required
          />
        </div>

        <div css={formRow}>
          <label>性別</label>
          <div css={radioGroup}>
            <label>
              <input
                type="radio"
                name="gender"
                value="male"
                checked={form.gender === 'male'}
                onChange={handleChange}
                required
              />
              男性
            </label>
            <label>
              <input
                type="radio"
                name="gender"
                value="female"
                checked={form.gender === 'female'}
                onChange={handleChange}
              />
              女性
            </label>
          </div>
        </div>

        <div css={formRow}>
          <label>月額保険料（円）</label>
          <input
            type="number"
            name="monthlyPremium"
            value={form.monthlyPremium}
            onChange={handleChange}
            placeholder="例: 10000"
            required
          />
        </div>

        <div css={formRow}>
          <label>払込年数</label>
          <select name="paymentYears" value={form.paymentYears} onChange={handleChange}>
            <option value="10">10年</option>
            <option value="15">15年</option>
            <option value="20">20年</option>
            <option value="30">30年</option>
          </select>
        </div>

        <div css={formRow}>
          <label>年金受取年数</label>
          <select name="pensionYears" value={form.pensionYears} onChange={handleChange}>
            <option value="10">10年</option>
            <option value="15">15年</option>
            <option value="20">20年</option>
          </select>
        </div>

        <button type="submit" css={submitButton(theme)}>見積もりする</button>
      </form>
    </section>
  )
}

const sectionStyle = css`
  padding: 4rem 1.5rem;
  background-color: #fffefc;
`

const titleStyle = css`
  font-size: 2rem;
  text-align: center;
  font-weight: 700;
  margin-bottom: 2rem;

  @media (max-width: 768px) {
    font-size: 1.5rem;
  }
`

const formStyle = css`
  max-width: 480px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`

const formRow = css`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;

  label {
    font-weight: 600;
    font-size: 0.95rem;
  }

  input,
  select {
    padding: 0.5rem 0.75rem;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 1rem;
  }
`

const radioGroup = css`
  display: flex;
  gap: 1.5rem;

  label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.95rem;
  }
`

const submitButton = (theme: any) => css`
  padding: 0.75rem 1rem;
  font-size: 1rem;
  font-weight: 700;
  background-color: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: ${theme.colors.primaryHover};
  }
`