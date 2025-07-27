/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import { useNavigate } from 'react-router-dom'
import Header from '@/components/Common/Header'
import Footer from '@/components/Common/Footer'
import { ContractSummary } from '@/components/ContractDetail/ContractSummary'
import { ContractConditions } from '@/components/ContractDetail/ContractConditions'
import { Beneficiaries } from '@/components/ContractDetail/Beneficiaries'
import { PaymentHistory } from '@/components/ContractDetail/PaymentHistory'
import { ContractActions } from '@/components/ContractDetail/ContractActions'
import { ContractPerformance } from '@/components/ContractDetail/ContractPerformance'
import { ContractChangeHistory } from '@/components/ContractDetail/ContractChangeHistory'
import { SupportInfo } from '@/components/ContractDetail/SupportInfo'

const ContractDetailPage = () => {
  const navigate = useNavigate()

  return (
    <>
      <Header />
      <main css={mainStyle}>
        <div css={backButtonWrapper}>
          <button onClick={() => navigate('/mypage')} css={backButton}>
            ← MyPageへ戻る
          </button>
        </div>

        <h1 css={titleStyle}>契約内容の詳細</h1>

        <ContractSummary />
        <ContractPerformance
          contractType="saving"
          totalPaid={120000}
          currentValue={140000}
        />
        <ContractConditions />
        <Beneficiaries />
        <PaymentHistory />
        <ContractChangeHistory />
        <ContractActions />
        <SupportInfo />
      </main>
      <Footer />
    </>
  )
}

export default ContractDetailPage

// ----------------------------
// Emotion CSS
// ----------------------------

const mainStyle = css`
  max-width: 960px;
  margin: 0 auto;
  padding: 3rem 1rem;
`

const titleStyle = css`
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 2rem;
  text-align: center;
`

const backButtonWrapper = css`
  display: flex;
  justify-content: flex-start;
  margin-bottom: 1.5rem;
`

const backButton = css`
  background: #f1f5f9;
  color: #1e3a8a;
  border: none;
  border-radius: 6px;
  padding: 0.6rem 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #e0e7ff;
  }
`