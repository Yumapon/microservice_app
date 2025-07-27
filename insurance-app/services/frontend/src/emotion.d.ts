// src/emotion.d.ts
import '@emotion/react'

declare module '@emotion/react' {
  export interface Theme {
    colors: {
      background: string
      surface: string
      primary: string
      primaryDark: string
      secondary: string
      text: string
      muted: string
      accent: string
      danger: string
    }
    spacing: {
      xs: string
      sm: string
      md: string
      lg: string
      xl: string
    }
    fontSize: {
      sm: string
      base: string
      lg: string
      xl: string
      title: string
    }
    radius: {
      sm: string
      md: string
      lg: string
      full: string
    }
  }
}