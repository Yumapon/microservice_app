/** @jsxImportSource @emotion/react */
import { useInitializeSession } from '@/hooks/useInitializeSession'

// セクションコンポーネント
import ApplicationSummarySection from '@/components/MyPage/ApplicationSummarySection'
import ContractSummarySection from '@/components/MyPage/ContractSummarySection'
import NotificationSection from '@/components/MyPage/NotificationSection'
import RecommendationSection from '@/components/MyPage/RecommendationSection'
import AccountAccessSection from '@/components/MyPage/AccountAccessSection'
import FaqAccessSection from '@/components/Common/FaqAccessSection'
import ContactAccessSection from '@/components/Common/ContactAccessSection'
import ProgressSection from '@/components/MyPage/ProgressSection'

import MyPageLayout from '@/components/layout/MyPageLayout'
import Container from '@/components/layout/Container'
import ThreeColumnWrapper from '@/components/layout/ThreeColumnWrapper'

const MyPage = () => {
    useInitializeSession()

    return (
        <MyPageLayout>
            <Container>
                <NotificationSection />
                <ContractSummarySection />
                <RecommendationSection />
                <ApplicationSummarySection />
                <ProgressSection />
                <ThreeColumnWrapper>
                    <AccountAccessSection />
                    <FaqAccessSection />
                    <ContactAccessSection />
                </ThreeColumnWrapper>
            </Container>
        </MyPageLayout>
    )
    }

export default MyPage