"""
AI Prediction Module
Fungsi: Machine Learning untuk prediksi risiko kredit macet

Model Features:
- Rasio pinjaman vs jaminan
- Lama gadai (hari)
- Outstanding pokok
- Histori outlet
- Kategori produk

Target Prediksi:
- Probabilitas kredit macet/lewat jatuh tempo
- Risk score (0-100)
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
from pathlib import Path
from config import OUTPUT_DIR, PROCESSED_FILE
from src.utils import print_section, print_stats


class GadaiRiskPredictor:
    """Machine Learning Model untuk prediksi risiko gadai"""
    
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.feature_importance = None
        self.model_path = OUTPUT_DIR / "risk_model.pkl"
        self.encoders_path = OUTPUT_DIR / "label_encoders.pkl"
        
    def prepare_features(self, df):
        """
        Prepare features untuk model ML
        
        Args:
            df: DataFrame dengan data gadai
            
        Returns:
            X: Features matrix
            y: Target variable (is_high_risk atau status_transaksi)
        """
        print_section("PREPARING ML FEATURES")
        
        # Copy dataframe
        df_ml = df.copy()
        
        # Handle missing values
        df_ml = df_ml.dropna(subset=['rasio_pinjaman', 'lama_gadai_hari', 'outstanding_pokok'])
        
        # Features dasar
        features = ['rasio_pinjaman', 'lama_gadai_hari', 'outstanding_pokok']
        
        # Encode categorical features
        categorical_features = []
        
        if 'outlet' in df_ml.columns:
            if 'outlet' not in self.label_encoders:
                self.label_encoders['outlet'] = LabelEncoder()
                df_ml['outlet_encoded'] = self.label_encoders['outlet'].fit_transform(df_ml['outlet'].astype(str))
            else:
                df_ml['outlet_encoded'] = self.label_encoders['outlet'].transform(df_ml['outlet'].astype(str))
            features.append('outlet_encoded')
            categorical_features.append('outlet')
        
        if 'kategori' in df_ml.columns:
            if 'kategori' not in self.label_encoders:
                self.label_encoders['kategori'] = LabelEncoder()
                df_ml['kategori_encoded'] = self.label_encoders['kategori'].fit_transform(df_ml['kategori'].astype(str))
            else:
                df_ml['kategori_encoded'] = self.label_encoders['kategori'].transform(df_ml['kategori'].astype(str))
            features.append('kategori_encoded')
            categorical_features.append('kategori')
        
        if 'segmen' in df_ml.columns:
            if 'segmen' not in self.label_encoders:
                self.label_encoders['segmen'] = LabelEncoder()
                df_ml['segmen_encoded'] = self.label_encoders['segmen'].fit_transform(df_ml['segmen'].astype(str))
            else:
                df_ml['segmen_encoded'] = self.label_encoders['segmen'].transform(df_ml['segmen'].astype(str))
            features.append('segmen_encoded')
            categorical_features.append('segmen')
        
        # Feature engineering tambahan
        if 'pokok pinjaman' in df_ml.columns and 'nilai jaminan' in df_ml.columns:
            df_ml['loan_to_value'] = df_ml['pokok pinjaman'] / (df_ml['nilai jaminan'] + 1)
            features.append('loan_to_value')
        
        # Target: is_high_risk atau status_transaksi == 'lewat_jt'
        if 'is_high_risk' in df_ml.columns:
            y = df_ml['is_high_risk'].astype(int)
        elif 'status_transaksi' in df_ml.columns:
            y = (df_ml['status_transaksi'] == 'lewat_jt').astype(int)
        else:
            raise ValueError("Tidak ada target variable yang tersedia")
        
        X = df_ml[features]
        
        print(f"✓ Features: {len(features)} kolom")
        print(f"  - Numeric: {len([f for f in features if 'encoded' not in f and f != 'loan_to_value'])}")
        print(f"  - Categorical (encoded): {len(categorical_features)}")
        print(f"  - Engineered: {'loan_to_value' if 'loan_to_value' in features else 'none'}")
        print(f"\n✓ Dataset size: {len(X):,} samples")
        print(f"  - Positive (Berisiko): {y.sum():,} ({y.sum()/len(y)*100:.1f}%)")
        print(f"  - Negative (Aman): {(~y.astype(bool)).sum():,} ({(~y.astype(bool)).sum()/len(y)*100:.1f}%)")
        
        return X, y, features
    
    def train(self, df, test_size=0.2, use_gradient_boosting=False):
        """
        Train model ML
        
        Args:
            df: DataFrame dengan data gadai
            test_size: Proporsi data test
            use_gradient_boosting: Gunakan Gradient Boosting (lebih akurat tapi lebih lambat)
            
        Returns:
            metrics: Dictionary dengan metrics evaluasi
        """
        print_section("TRAINING ML MODEL")
        
        # Prepare features
        X, y, feature_names = self.prepare_features(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"\n✓ Data split:")
        print(f"  - Training: {len(X_train):,} samples")
        print(f"  - Testing: {len(X_test):,} samples")
        
        # Train model
        print(f"\n⏳ Training model...")
        if use_gradient_boosting:
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
            print(f"  Model: Gradient Boosting Classifier")
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            print(f"  Model: Random Forest Classifier")
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Metrics
        accuracy = (y_pred == y_test).mean()
        try:
            roc_auc = roc_auc_score(y_test, y_pred_proba)
        except:
            roc_auc = 0.0
        
        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n✓ Model trained successfully!")
        print(f"\n📊 Model Performance:")
        print(f"  - Accuracy: {accuracy*100:.2f}%")
        print(f"  - ROC-AUC Score: {roc_auc:.4f}")
        
        print(f"\n🎯 Top 5 Most Important Features:")
        for idx, row in self.feature_importance.head().iterrows():
            print(f"  {idx+1}. {row['feature']:20} : {row['importance']:.4f}")
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\n📈 Confusion Matrix:")
        print(f"  True Negative:  {cm[0,0]:,}")
        print(f"  False Positive: {cm[0,1]:,}")
        print(f"  False Negative: {cm[1,0]:,}")
        print(f"  True Positive:  {cm[1,1]:,}")
        
        metrics = {
            'accuracy': accuracy,
            'roc_auc': roc_auc,
            'confusion_matrix': cm.tolist(),
            'feature_importance': self.feature_importance.to_dict('records')
        }
        
        return metrics
    
    def predict(self, df):
        """
        Prediksi risiko untuk data baru
        
        Args:
            df: DataFrame dengan data yang akan diprediksi
            
        Returns:
            predictions: DataFrame dengan hasil prediksi
        """
        if self.model is None:
            raise ValueError("Model belum di-train! Jalankan train() terlebih dahulu.")
        
        X, _, _ = self.prepare_features(df)
        
        # Predict
        y_pred = self.model.predict(X)
        y_pred_proba = self.model.predict_proba(X)[:, 1]
        
        # Risk score (0-100)
        risk_score = (y_pred_proba * 100).astype(int)
        
        # Risk category
        def categorize_risk(score):
            if score < 30:
                return "Rendah"
            elif score < 70:
                return "Sedang"
            else:
                return "Tinggi"
        
        predictions = pd.DataFrame({
            'is_risky': y_pred,
            'risk_probability': y_pred_proba,
            'risk_score': risk_score,
            'risk_category': [categorize_risk(s) for s in risk_score]
        })
        
        return predictions
    
    def save_model(self):
        """Simpan model dan encoders ke file"""
        if self.model is None:
            raise ValueError("Model belum di-train!")
        
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.label_encoders, self.encoders_path)
        
        print(f"\n✓ Model saved: {self.model_path.name}")
        print(f"✓ Encoders saved: {self.encoders_path.name}")
    
    def load_model(self):
        """Load model dan encoders dari file"""
        if not self.model_path.exists():
            raise FileNotFoundError("Model file tidak ditemukan!")
        
        self.model = joblib.load(self.model_path)
        self.label_encoders = joblib.load(self.encoders_path)
        
        print(f"✓ Model loaded: {self.model_path.name}")


def train_and_save_model(df_path=PROCESSED_FILE):
    """
    Helper function: Train model dan simpan
    
    Args:
        df_path: Path ke file data processed
    """
    # Load data
    df = pd.read_csv(df_path)
    
    # Initialize predictor
    predictor = GadaiRiskPredictor()
    
    # Train
    metrics = predictor.train(df, test_size=0.2)
    
    # Save
    predictor.save_model()
    
    return predictor, metrics


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  AI PREDICTION MODEL - TRAINING")
    print("="*60)
    
    predictor, metrics = train_and_save_model()
    
    print("\n" + "="*60)
    print("  ✓ TRAINING SELESAI")
    print("="*60)
    print(f"\nAccuracy: {metrics['accuracy']*100:.2f}%")
    print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    print("\n")
