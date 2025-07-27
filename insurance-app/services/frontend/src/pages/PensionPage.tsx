import { PensionHero } from '@/components/DetailPage/PensionHero'
import { PensionFeatures } from '@/components/DetailPage/PensionFeatures'
import { PensionSimulation } from '@/components/DetailPage/PensionSimulation'
import { PensionFaq } from '@/components/DetailPage/PensionFaq'
import Header from '@/components/Common/Header'
import Footer from '@/components/Common/Footer'

const PensionPage = () => {
  return (
    <>
      <Header />
      <main>
        <PensionHero />
        <PensionFeatures />
        <PensionSimulation />
        <PensionFaq />
      </main>
      <Footer />
    </>
  )
}

export default PensionPage