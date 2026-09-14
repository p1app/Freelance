import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
    components,
    directives,
    theme: {
        defaultTheme: 'dark',
        themes: {
            dark: {
                dark: true,
                colors: {
                    primary: '#3B82F6',
                    'primary-darken-1': '#1E40AF',
                    'primary-lighten-1': '#60A5FA',
                    secondary: '#1F2937',
                    'secondary-darken-1': '#111827',
                    accent: '#8B5CF6',
                    error: '#EF4444',
                    info: '#3B82F6',
                    success: '#10B981',
                    warning: '#F59E0B',
                    background: '#0A0E1A',
                    surface: '#111827',
                    'surface-light': '#1F2937',
                    'surface-variant': '#374151',
                    'on-surface': '#F9FAFB',
                    'on-surface-variant': '#9CA3AF',
                    'on-background': '#F9FAFB',
                },
            },
        },
    },
    defaults: {
        VBtn: {
            rounded: 'lg',
            elevation: 0,
            style: 'text-transform: none; letter-spacing: 0; font-weight: 600;',
        },
        VCard: {
            rounded: 'xl',
            elevation: 0,
            style: 'border: 1px solid rgba(59, 130, 246, 0.1);',
        },
        VTextField: {
            variant: 'outlined',
            density: 'comfortable',
            rounded: 'lg',
        },
        VSelect: {
            variant: 'outlined',
            density: 'comfortable',
            rounded: 'lg',
        },
        VTextarea: {
            variant: 'outlined',
            density: 'comfortable',
            rounded: 'lg',
        },
        VChip: {
            rounded: 'lg',
        },
        VDialog: {
            rounded: 'xl',
        },
    },
})

export default vuetify