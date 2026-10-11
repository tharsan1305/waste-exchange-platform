import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      appName: "Waste Exchange Platform",
      tagline: "One Industry's Waste is Another Industry's Raw Material",
      nav: {
        marketplace: "Marketplace",
        network: "Symbiosis Network",
        deals: "Deal Room",
        dashboard: "Dashboard",
        login: "Sign In",
        register: "Register Industry"
      },
      hero: {
        title: "Industrial Symbiosis Marketplace",
        subtitle: "Monetize industrial production byproducts directly with manufacturing plants that use them as raw materials. Zero brokers. 100% compliant.",
        exploreListings: "Browse Waste Listings",
        registerNow: "Register Your Plant",
        verifiedPlants: "Verified Industries",
        co2Mitigated: "Tonnes CO₂ Mitigated",
        landfillDiverted: "Tonnes Landfill Diverted"
      },
      listings: {
        filterCategory: "Waste Category",
        searchPlaceholder: "Search bagasse, fly ash, steel slag...",
        matchScore: "Symbiosis Fit",
        viewSpecs: "View Specifications & Passport"
      }
    }
  },
  ta: {
    translation: {
      appName: "வேஸ்ட் எக்ஸ்சேஞ்ச் பிளாட்ஃபார்ம்",
      tagline: "ஒரு தொழிற்சாலையின் கழிவு, மற்றொரு தொழிற்சாலையின் மூலப்பொருள்",
      nav: {
        marketplace: "சந்தைப்பகுதி",
        network: "தொழில்முறை நெட்வொர்க்",
        deals: "ஒப்பந்த அறை",
        dashboard: "டாஷ்போர்டு",
        login: "உள்நுழைவு",
        register: "தொழிற்சாலை பதிவு"
      },
      hero: {
        title: "தொழிலக கழிவு மறுபயன்பாட்டு தளம்",
        subtitle: "உங்கள் தொழிற்சாலை உபரி கழிவுகளை நேரடியாக தேவைப்படும் பிற தொழிற்சாலைகளுக்கு மாற்றி லாபம் ஈட்டுங்கள். இடைத்தரகர்கள் இல்லை.",
        exploreListings: "கழிவுகளை பார்வையிடுங்கள்",
        registerNow: "பதிவு செய்யுங்கள்",
        verifiedPlants: "சரிபார்க்கப்பட்ட நிறுவனங்கள்",
        co2Mitigated: "டன் CO₂ சேமிப்பு",
        landfillDiverted: "டன் குப்பை சேமிப்பு"
      },
      listings: {
        filterCategory: "கழிவு வகை",
        searchPlaceholder: "பகாஸ், பிளை ஆஷ், ஸ்லாக் தேடுங்கள்...",
        matchScore: "பொருத்த அளவு",
        viewSpecs: "விவரங்களை பார்க்க"
      }
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
