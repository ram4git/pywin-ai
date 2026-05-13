export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#006EE5', 'primary-light': '#E8F4FD', 'primary-dark': '#0055B3',
        background: '#FCFDFF', surface: '#FFFFFF', 'surface-secondary': '#F2FAFF',
        border: '#E2E8F0', 'border-light': '#F0F4F8',
        'text-primary': '#06192D', 'text-secondary': '#4A5568', 'text-muted': '#8896A6',
        success: '#10B981', error: '#EF4444', warning: '#F59E0B',
      },
      fontFamily: { sans: ['Manrope', 'Inter', 'sans-serif'] },
      boxShadow: { card: '0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)', 'card-hover': '0 10px 15px -3px rgba(0,0,0,0.1)' },
    },
  },
  plugins: [],
}
