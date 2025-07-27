/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { useState } from 'react'

export const ContactForm = () => {
  const theme = useTheme()

  const [form, setForm] = useState({
    name: '',
    email: '',
    message: '',
  })

  const [errors, setErrors] = useState({
    name: '',
    email: '',
    message: '',
  })

  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const validateField = (name: string, value: string): string => {
    switch (name) {
      case 'name':
        return value.trim() ? '' : 'お名前を入力してください。'
      case 'email':
        if (!value.trim()) return 'メールアドレスを入力してください。'
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return '有効なメールアドレスを入力してください。'
        return ''
      case 'message':
        return value.trim() ? '' : 'お問い合わせ内容を入力してください。'
      default:
        return ''
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
    const error = validateField(name, value)
    setErrors((prev) => ({ ...prev, [name]: error }))
  }

  const validateAll = () => {
    const newErrors = {
      name: validateField('name', form.name),
      email: validateField('email', form.email),
      message: validateField('message', form.message),
    }
    setErrors(newErrors)
    return Object.values(newErrors).every((err) => err === '')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validateAll()) return

    setLoading(true)
    setSuccess(false)
    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })

      if (!response.ok) throw new Error('送信に失敗しました')

      setSuccess(true)
      setForm({ name: '', email: '', message: '' })
      setErrors({ name: '', email: '', message: '' })
    } catch (err) {
      alert('送信に失敗しました。時間をおいて再度お試しください。')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section css={formSection}>
      <form onSubmit={handleSubmit} css={formStyle} noValidate>
        <div css={formRow}>
          <label htmlFor="name">お名前</label>
          <input
            type="text"
            id="name"
            name="name"
            value={form.name}
            onChange={handleChange}
            css={[inputBase, errors.name && errorInput]}
          />
          {errors.name && <p css={errorText}>{errors.name}</p>}
        </div>

        <div css={formRow}>
          <label htmlFor="email">メールアドレス</label>
          <input
            type="email"
            id="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            css={[inputBase, errors.email && errorInput]}
          />
          {errors.email && <p css={errorText}>{errors.email}</p>}
        </div>

        <div css={formRow}>
          <label htmlFor="message">お問い合わせ内容</label>
          <textarea
            id="message"
            name="message"
            rows={6}
            value={form.message}
            onChange={handleChange}
            css={[inputBase, errors.message && errorInput]}
            placeholder="例）保険のプランについて詳しく知りたいです。"
          />
          {errors.message && <p css={errorText}>{errors.message}</p>}
        </div>

        <button type="submit" css={submitButton(theme)} disabled={loading}>
          {loading ? '送信中...' : '送信する'}
        </button>

        {success && <p css={successMessage}>送信が完了しました。ありがとうございました！</p>}
      </form>
    </section>
  )
}

const formSection = css`
  padding: 4rem 1.5rem;
  background-color: #fff;
`

const formStyle = css`
  max-width: 600px;
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
`

const inputBase = css`
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
`

const errorInput = css`
  border-color: #e53935;
  background-color: #fff6f6;
`

const errorText = css`
  color: #e53935;
  font-size: 0.85rem;
`

const successMessage = css`
  color: #2e7d32;
  font-size: 0.95rem;
  margin-top: 1rem;
  font-weight: 600;
`

const submitButton = (theme: any) => css`
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 700;
  background-color: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover:enabled {
    background-color: ${theme.colors.primaryHover};
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`