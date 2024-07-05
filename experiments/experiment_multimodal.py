from recommender_systems.multimodal_recommender import MultimodalRecommender
import numpy as np

def run_experiment():
    text_features = np.random.rand(1000, 300)
    image_features = np.random.rand(1000, 2048)
    video_features = np.random.rand(1000, 4096)
    user_profile = np.random.rand(1, 300 + 2048 + 4096)
    recommender = MultimodalRecommender(text_features, image_features, video_features)
    recommendations = recommender.recommend(user_profile, top_n=5)
    print(f"Top 5 Multimodal Recommendations: {recommendations}")

if __name__ == "__main__":
    run_experiment()
