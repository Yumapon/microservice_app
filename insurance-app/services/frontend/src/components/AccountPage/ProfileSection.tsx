/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { useEffect, useState } from 'react'

type UserProfile = {
  name: string
  email: string
  birthDate: string
  address: string
}

const mockProfile: UserProfile = {
  name: '山田 太郎',
  email: 'taro.yamada@example.com',
  birthDate: '1990-05-10',
  address: '東京都新宿区西新宿1-1-1',
}

const ProfileSection = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null)

  useEffect(() => {
    // TODO: 将来的にAPIから取得
    setProfile(mockProfile)
  }, [])

  if (!profile) return null

  return (
    <section css={sectionStyle}>
      <h2 css={titleStyle}>ご本人情報</h2>
      <div css={cardStyle}>
        <div css={infoRow}>
          <span css={label}>氏名：</span>
          <span>{profile.name}</span>
        </div>
        <div css={infoRow}>
          <span css={label}>メールアドレス：</span>
          <span>{profile.email}</span>
        </div>
        <div css={infoRow}>
          <span css={label}>生年月日：</span>
          <span>{profile.birthDate}</span>
        </div>
        <div css={infoRow}>
          <span css={label}>住所：</span>
          <span>{profile.address}</span>
        </div>
        <div css={buttonRow}>
          <button css={editButton} onClick={() => alert('編集画面へ遷移予定')}>
            情報を編集する
          </button>
        </div>
      </div>
    </section>
  )
}

export default ProfileSection

// ------------------------
// CSS-in-JS
// ------------------------
const sectionStyle = css`
  padding: 1rem 0;
`

const titleStyle = css`
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
`

const cardStyle = css`
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  background-color: #f9f9f9;
`

const infoRow = css`
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
`

const label = css`
  font-weight: bold;
  min-width: 6rem;
`

const buttonRow = css`
  margin-top: 1rem;
  text-align: right;
`

const editButton = css`
  background-color: #0ea5e9;
  color: white;
  border: none;
  padding: 0.4rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;

  &:hover {
    background-color: #0369a1;
  }
`