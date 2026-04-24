# Solar Energy Production Zone Clustering

##  Overview
This project identifies high-potential solar energy zones by clustering geographical regions based on energy production characteristics. It combines data analysis, machine learning, and interactive visualization to support data-driven decision-making.



## Business Objective
The goal is to help energy companies:
- Identify **high ROI regions**
- Improve **project feasibility analysis**
- Enable **strategic expansion planning**

---

## Approach

### 1. Data Processing
- Cleaned and preprocessed large-scale solar project data  
- Handled missing values and duplicates  
- Created meaningful features:
  - Energy per kW  
  - Capacity Factor  
  - Average Project Size  

---

### 2. Clustering Models
Implemented and compared:
- K-Means (final model)  
- Hierarchical Clustering  
- DBSCAN  

### Model Evaluation Metrics
- Silhouette Score  
- Davies-Bouldin Index  
- Calinski-Harabasz Index  

 **K-Means was selected** for its scalability, stability, and interpretability.

---

### 3. Cluster Interpretation

- 🟢 **High Production Zone**  
  High efficiency and strong solar potential → ideal for investment  

- 🔵 **Medium Production Zone**  
  Moderate performance → optimization opportunities  

- 🔴 **Low Production Zone**  
  Lower efficiency → limited large-scale viability  

---

## Dashboard Features (Streamlit)

- Interactive map with cluster visualization  
- Heatmap of energy production  
- KPI metrics (energy, projects, coverage)  
- Time-series cluster trends  
- ZIP code search  
- Developer & utility analysis  
- Business recommendations  
- Live Link : https://solar-energy-appuction-clustering-jtjjappjkqehpvdcs32sjbw.streamlit.app/
---

## 🛠️ Tech Stack

- Python  
- Pandas, NumPy  
- Scikit-learn  
- Plotly  
- Folium  
- Streamlit  

---

