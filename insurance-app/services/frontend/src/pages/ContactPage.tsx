import Header from '@/components/Common/Header'
import Footer from '@/components/Common/Footer'
import { ContactHero } from '@/components/ContactPage/ContactHero'
import { ContactForm } from '@/components/ContactPage/ContactForm'

const ContactPage = () => {
  return (
    <>
      <Header />
      <main>
        <ContactHero />
        <ContactForm />
      </main>
      <Footer />
    </>
  )
}

export default ContactPage