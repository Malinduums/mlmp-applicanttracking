import string
import numpy as np
import faiss
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class AdvancedJobRecommendationSystem:
    def __init__(self, jobs_data):
        """Initialize the advanced ML system with job data"""
        self.jobs_data = jobs_data
        self.jobs_texts = []
        self.job_embeddings = None
        self.tfidf_vectorizer = None
        self.faiss_index = None
        
        # Load Sentence Transformer model
        try:
            self.sentence_model = SentenceTransformer("paraphrase-MiniLM-L6-v2", device="cpu")
            # Quantize for better performance
            self.sentence_model = torch.quantization.quantize_dynamic(
                self.sentence_model, {torch.nn.Linear}, dtype=torch.qint8
            )
            logger.info("✅ Sentence Transformer model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Error loading Sentence Transformer: {str(e)}")
            self.sentence_model = None
        
        self._prepare_job_data()
        self._build_embeddings()
        self._build_faiss_index()
    
    def _prepare_job_data(self):
        """Prepare job text data for ML processing"""
        for job in self.jobs_data:
            job_text = f"{job.position} {job.workplace} {job.working_mode} {job.job_role_and_duties} {job.requisite_skill}"
            self.jobs_texts.append(self._clean_text(job_text))
        
        logger.info(f"✅ Prepared {len(self.jobs_texts)} job texts for ML processing")
    
    def _clean_text(self, text):
        """Clean text for ML processing"""
        return text.lower().translate(str.maketrans("", "", string.punctuation)).strip()
    
    def _build_embeddings(self):
        """Build sentence embeddings for all jobs"""
        if self.sentence_model is None:
            logger.warning("⚠️ Sentence Transformer not available, using TF-IDF only")
            return
        
        try:
            self.job_embeddings = self.sentence_model.encode(
                self.jobs_texts, convert_to_numpy=True
            ).astype(np.float16)
            logger.info(f"✅ Built embeddings for {len(self.jobs_texts)} jobs")
        except Exception as e:
            logger.error(f"❌ Error building embeddings: {str(e)}")
            self.job_embeddings = None
    
    def _build_faiss_index(self):
        """Build FAISS index for fast similarity search"""
        if self.job_embeddings is None:
            logger.warning("⚠️ No embeddings available, skipping FAISS index")
            return
        
        try:
            self.dim = self.job_embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(self.dim)
            self.faiss_index.add(self.job_embeddings.astype(np.float16))
            logger.info("✅ FAISS index built successfully")
        except Exception as e:
            logger.error(f"❌ Error building FAISS index: {str(e)}")
            self.faiss_index = None
    
    def _build_tfidf_features(self):
        """Build TF-IDF features for jobs"""
        try:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.jobs_texts)
            logger.info("✅ TF-IDF features built successfully")
        except Exception as e:
            logger.error(f"❌ Error building TF-IDF features: {str(e)}")
            self.tfidf_vectorizer = None
    
    def get_tfidf_recommendations(self, resume_text, top_n=20):
        """Get recommendations using TF-IDF + Cosine Similarity"""
        if self.tfidf_vectorizer is None:
            self._build_tfidf_features()
        
        if self.tfidf_vectorizer is None:
            logger.error("❌ TF-IDF vectorizer not available")
            return []
        
        try:
            # Clean resume text
            clean_resume = self._clean_text(resume_text)
            
            # Transform resume to TF-IDF vector
            resume_vector = self.tfidf_vectorizer.transform([clean_resume])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(resume_vector, self.tfidf_matrix).flatten()
            
            # Get top recommendations
            top_indices = np.argsort(similarities)[-top_n:][::-1]
            
            recommendations = []
            for idx in top_indices:
                job = self.jobs_data[idx]
                recommendations.append({
                    'position': job.position,
                    'workplace': job.workplace,
                    'working_mode': job.working_mode,
                    'job_role_and_duties': job.job_role_and_duties,
                    'requisite_skill': job.requisite_skill,
                    'salary_min': float(job.salary_min) if job.salary_min else None,
                    'salary_max': float(job.salary_max) if job.salary_max else None,
                    'location': job.location,
                    'similarity_score': round(similarities[idx] * 100, 1),
                    'ai_ranked': True,
                    'method': 'TF-IDF + Cosine Similarity'
                })
            
            logger.info(f"✅ TF-IDF recommendations: {len(recommendations)} jobs")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error in TF-IDF recommendations: {str(e)}")
            return []
    
    def get_semantic_recommendations(self, resume_text, top_n=20):
        """Get recommendations using Sentence Transformers + FAISS"""
        if self.faiss_index is None or self.sentence_model is None:
            logger.warning("⚠️ Semantic search not available, falling back to TF-IDF")
            return self.get_tfidf_recommendations(resume_text, top_n)
        
        try:
            # Clean resume text
            clean_resume = self._clean_text(resume_text)
            
            # Get resume embedding
            resume_embedding = self.sentence_model.encode(
                [clean_resume], convert_to_numpy=True
            ).astype(np.float16)
            
            # Search FAISS index
            distances, indices = self.faiss_index.search(resume_embedding, top_n)
            
            recommendations = []
            for i, idx in enumerate(indices[0]):
                job = self.jobs_data[idx]
                # Convert distance to similarity score (0-100)
                similarity_score = max(0, min(100, (1 - distances[0][i]) * 100))
                
                recommendations.append({
                    'position': job.position,
                    'workplace': job.workplace,
                    'working_mode': job.working_mode,
                    'job_role_and_duties': job.job_role_and_duties,
                    'requisite_skill': job.requisite_skill,
                    'salary_min': float(job.salary_min) if job.salary_min else None,
                    'salary_max': float(job.salary_max) if job.salary_max else None,
                    'location': job.location,
                    'similarity_score': round(similarity_score, 1),
                    'ai_ranked': True,
                    'method': 'Semantic Search (BERT)'
                })
            
            logger.info(f"✅ Semantic recommendations: {len(recommendations)} jobs")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error in semantic recommendations: {str(e)}")
            return self.get_tfidf_recommendations(resume_text, top_n)
    
    def get_hybrid_recommendations(self, resume_text, top_n=20):
        """Get recommendations using both TF-IDF and Semantic methods"""
        tfidf_recs = self.get_tfidf_recommendations(resume_text, top_n)
        semantic_recs = self.get_semantic_recommendations(resume_text, top_n)
        
        # Combine and rank by average score
        job_scores = {}
        
        # Add TF-IDF scores
        for rec in tfidf_recs:
            job_key = f"{rec['position']}_{rec['workplace']}"
            if job_key not in job_scores:
                job_scores[job_key] = {'job': rec, 'scores': []}
            job_scores[job_key]['scores'].append(rec['similarity_score'])
        
        # Add semantic scores
        for rec in semantic_recs:
            job_key = f"{rec['position']}_{rec['workplace']}"
            if job_key not in job_scores:
                job_scores[job_key] = {'job': rec, 'scores': []}
            job_scores[job_key]['scores'].append(rec['similarity_score'])
        
        # Calculate average scores
        hybrid_recommendations = []
        for job_key, data in job_scores.items():
            avg_score = sum(data['scores']) / len(data['scores'])
            job = data['job'].copy()
            job['similarity_score'] = round(avg_score, 1)
            job['method'] = 'Hybrid (TF-IDF + BERT)'
            hybrid_recommendations.append(job)
        
        # Sort by average score
        hybrid_recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        logger.info(f"✅ Hybrid recommendations: {len(hybrid_recommendations)} jobs")
        return hybrid_recommendations[:top_n] 