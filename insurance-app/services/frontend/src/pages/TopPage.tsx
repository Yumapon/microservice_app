// セクションコンポーネント
import { ProductSection } from '@/components/TopPage/ProductSection'
import { DiagnosisSection } from '@/components/TopPage/DiagnosisSection'
import { CtaSection } from '@/components/TopPage/CtaSection'
import { FlowSection } from '@/components/TopPage/FlowSection'

import FaqAccessSection from '@/components/Common/FaqAccessSection'
import ContactAccessSection from '@/components/Common/ContactAccessSection'

import TopPageLayout from '@/components/layout/TopPageLayout'
import Container from '@/components/layout/Container'
import TwoColumnWrapper from '@/components/layout/TwoColumnWrapper'

const TopPage = () => {
  return (
   <TopPageLayout>
    <Container>
      <CtaSection />
      <FlowSection />
      <ProductSection />
      <DiagnosisSection />
      <TwoColumnWrapper>
        <FaqAccessSection />
        <ContactAccessSection />
      </TwoColumnWrapper>
    </Container>
  </TopPageLayout>
  )
}

export default TopPage