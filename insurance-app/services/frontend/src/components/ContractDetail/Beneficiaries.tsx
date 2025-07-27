/** @jsxImportSource @emotion/react */
import { css, useTheme } from '@emotion/react'
import { FaUserFriends } from 'react-icons/fa'

const mockData = [
  // 空配列にすればメッセージが表示されます
  {
    name: '佐々木花子',
    relation: '配偶者',
    allocation: 50,
    note: '優先受取人',
  },
  {
    name: '佐々木太郎',
    relation: '子1',
    allocation: 30,
    note: '第1受取人',
  },
  {
    name: '佐々木太郎2',
    relation: '子2',
    allocation: 20,
    note: '第2受取人',
  },
]

export const Beneficiaries = () => {
  const theme = useTheme()
  const sorted = [...mockData].sort((a, b) => b.allocation - a.allocation)

  return (
    <section css={sectionWrapper}>
      <h2 css={titleStyle(theme)}>
        <FaUserFriends style={{ marginRight: '0.5rem' }} />
        保険金受取人
      </h2>

      {sorted.length === 0 ? (
        <p css={emptyMessage}>代理受取人が設定されていません。</p>
      ) : (
        <div css={cardContainer}>
          {sorted.map((b, idx) => (
            <div key={idx} css={cardStyle(theme)}>
              <div css={headerBlock}>
                <span css={allocationBadge}>{b.allocation}%</span>
              </div>
              <div css={infoBlock}>
                <p><strong>氏名：</strong>{b.name}</p>
                <p><strong>続柄：</strong>{b.relation}</p>
                {b.note && <p><strong>備考：</strong>{b.note}</p>}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

// ----------------------------
// Emotion スタイル定義
// ----------------------------

const sectionWrapper = css`
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

const cardContainer = css`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
`

const cardStyle = (theme: any) => css`
  background-color: ${theme.colors.tile};
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
`

const headerBlock = css`
  display: flex;
  justify-content: flex-end;
`

const allocationBadge = css`
  background-color: #4caf50;
  color: white;
  padding: 0.4rem 0.75rem;
  font-size: 0.9rem;
  font-weight: 700;
  border-radius: 9999px;
`

const infoBlock = css`
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;

  p {
    font-size: 0.95rem;
    line-height: 1.5;
  }
`

const emptyMessage = css`
  text-align: center;
  font-size: 1rem;
  color: #888;
  background-color: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
  border: 1px dashed #ccc;
`