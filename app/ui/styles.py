# app/ui/styles.py
def inject_custom_css():
    """Inyecta CSS personalizado en la aplicación"""
    st.markdown("""
    <style>
        .stApp { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .main-header { 
            background: rgba(255, 255, 255, 0.95); 
            padding: 1.5rem; 
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            margin-bottom: 2rem;
        }
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            border-left: 4px solid #2E7D32;
            margin: 8px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .metric-title { 
            color: #2C3E50; 
            font-size: 14px; 
            font-weight: 500; 
            margin-bottom: 8px; 
        }
        .metric-value { 
            color: #2E7D32; 
            font-size: 28px; 
            font-weight: 700; 
            margin: 0; 
        }
        .metric-delta { 
            color: #4CAF50; 
            font-size: 14px; 
            margin-top: 4px; 
        }
        .stButton>button {
            background-color: #2E7D32;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: 500;
        }
        .stButton>button:hover {
            background-color: #1B5E20;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)
