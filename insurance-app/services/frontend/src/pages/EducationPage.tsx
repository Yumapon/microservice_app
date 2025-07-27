import Header from '@/components/Common/Header'
import Footer from '@/components/Common/Footer'
import { EducationHero } from '@/components/DetailPage/EducationHero'
import { EducationFeatures } from '@/components/DetailPage/EducationFeatures'
import { EducationSimulation } from '@/components/DetailPage/EducationSimulation'
import { EducationFaq } from '@/components/DetailPage/EducationFaq'

const EducationPage = () => {
  return (
    <>
      <Header />
      <main>
        <EducationHero />
        <EducationFeatures />
        <EducationSimulation />
        <EducationFaq />
      </main>
      <Footer />
    </>
  )
}

export default EducationPage