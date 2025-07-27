/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { useState, useEffect } from 'react'
import { format } from 'date-fns'
import { useNavigate } from 'react-router-dom'

type ApplicationProgress = {
  id: string
  planName: string
  currentStep: 'quote' | 'application' | 'identity' | 'confirmed'
  createdAt: string
}

const stepLabels = [
  { key: 'quote', label: '見積もり済み' },
  { key: 'application', label: '申込情報入力' },
  { key: 'identity', label: '本人確認' },
  { key: 'confirmed', label: '契約完了' },
]

const mockApplications: ApplicationProgress[] = [
  {
    id: 'app-001',
    planName: '個人年金保険',
    currentStep: 'quote',
    createdAt: '2025-07-01T10:30:00',
  },
  {
    id: 'app-002',
    planName: '医療保険（入院日額5,000円）',
    currentStep: 'application',
    createdAt: '2025-07-05T14:00:00',
  },
  {
    id: 'app-003',
    planName: 'がん保険（診断一時金型）',
    currentStep: 'identity',
    createdAt: '2025-07-10T09:15:00',
  },
  {
    id: 'app-004',
    planName: '終身保険（貯蓄型）',
    currentStep: 'confirmed',
    createdAt: '2025-06-20T08:45:00',
  },
]

export const ApplicationSummarySection = () => {
  const [applications, setApplications] = useState<ApplicationProgress[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    const activeApplications = mockApplications.filter(app => app.currentStep !== 'confirmed')
    setApplications(activeApplications)
  }, [])

  return (
    <section css={sectionStyle}>
      <h2 css={titleStyle}>お申込み中の保険</h2>

      {applications.length === 0 ? (
        <p css={emptyTextStyle}>お申込中の保険はありません。</p>
      ) : (
        <div css={cardContainer}>
          {applications.map((app) => {
            const currentIndex = getStepIndex(app.currentStep)
            return (
              <div
                key={app.id}
                css={flowBox}
                onClick={() => navigate(`/applications/${app.id}`)}
              >
                <h3 css={planTitle}>「{app.planName}」の申込進捗</h3>
                <p css={dateText}>申込日：{format(new Date(app.createdAt), 'yyyy年MM月dd日')}</p>
                <ol css={stepList}>
                  {stepLabels.map((step, index) => {
                    const isActive = index === currentIndex
                    const isComplete = index < currentIndex
                    return (
                      <li key={step.key} css={stepItem(isActive, isComplete)}>
                        {isComplete ? '✔ ' : ''}
                        {step.label}
                      </li>
                    )
                  })}
                </ol>
                {app.currentStep !== 'confirmed' && (
                  <div css={buttonBox}>{renderNextAction(app.currentStep)}</div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}

export default ApplicationSummarySection

// ----------------------------
// ロジック補助関数
// ----------------------------
const getStepIndex = (step: ApplicationProgress['currentStep']) => {
  return stepLabels.findIndex((s) => s.key === step)
}

const renderNextAction = (step: ApplicationProgress['currentStep']) => {
  let primaryLabel = ''
  switch (step) {
    case 'quote':
      primaryLabel = '申込をはじめる'
      break
    case 'application':
      primaryLabel = '本人確認へ進む'
      break
    case 'identity':
      primaryLabel = '契約手続きへ進む'
      break
    default:
      return null
  }

  return (
    <div css={buttonRow}>
      <button css={cancelButton}>キャンセル</button>
      <button css={actionButton}>{primaryLabel}</button>
    </div>
  )
}

// ----------------------------
// スタイル定義
// ----------------------------
const sectionStyle = css`
  padding: 1rem 0;
`

const titleStyle = css`
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
`

const cardContainer = css`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`

const flowBox = css`
  background: #ffffff;
  padding: 1rem;
  padding-top: 3rem;
  border-radius: 8px;
  border: 1px solid #ddd;
  position: relative;
  cursor: pointer;
  transition: box-shadow 0.2s ease;

  &:hover {
    box-shadow: 0 0 0 2px #bae6fd;
  }

  @media (max-width: 767px) {
    padding-top: 1rem;
  }
`

const planTitle = css`
  font-size: 1rem;
  font-weight: bold;
`

const dateText = css`
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.25rem;
`

const stepList = css`
  list-style: none;
  display: flex;
  justify-content: space-between;
  padding: 0;
  margin: 1rem 0 0.5rem;
`

const stepItem = (active: boolean, complete: boolean) => css`
  flex: 1;
  text-align: center;
  font-weight: ${active ? 'bold' : 'normal'};
  color: ${active ? '#0ea5e9' : complete ? '#22c55e' : '#999'};
  position: relative;

  &::after {
    content: '';
    display: block;
    margin: 0.3rem auto;
    width: 8px;
    height: 8px;
    background: ${active ? '#0ea5e9' : complete ? '#22c55e' : '#ccc'};
    border-radius: 9999px;
  }
`

const buttonBox = css`
  position: absolute;
  top: 1rem;
  right: 1rem;

  @media (max-width: 767px) {
    position: static;
    margin-top: 1rem;
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
  }
`

const actionButton = css`
  padding: 0.4rem 0.8rem;
  background: #0ea5e9;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  min-width: 8rem;
  text-align: center;

  &:hover {
    background: rgb(119, 194, 228);
  }
`

const emptyTextStyle = css`
  color: #888;
  font-size: 1rem;
  text-align: center;
  margin: 2rem 0;
`

const buttonRow = css`
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.5rem;
`

const cancelButton = css`
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  color: #ef4444;
  border: 1px solid #ef4444;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;

  &:hover {
    background: #fee2e2;
  }

  @media (max-width: 767px) {
    margin-left: 0;
  }
`