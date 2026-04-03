import os
from PIL import Image
from sentence_transformers import SentenceTransformer, util
import torch

class ImageAnalyzer:
    def __init__(self, model_name='clip-ViT-B-32'):
        # Vi laddar CLIP-modellen. Första gången tar det lite tid (den laddas ner).
        # 'clip-ViT-B-32' är en bra balans mellan snabbhet och precision.
        self.model = SentenceTransformer(model_name)
        self.image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')

    def find_duplicates(self, folder_path, threshold=0.95):
        """
        Går igenom mappen, skapar embeddings och hittar likheter.
        """
        # 1. Hitta alla bildfiler
        image_paths = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(self.image_extensions)
        ]

        if not image_paths:
            return []

        # 2. Skapa 'embeddings' (AI-analysen)
        # Vi använder Pillow för att öppna bilderna
        images = [Image.open(p) for p in image_paths]
        embeddings = self.model.encode(images, convert_to_tensor=True, show_progress_bar=True)

        # 3. Jämför alla bilder med varandra (Cosine Similarity)
        # Detta skapar en matris med likhetspoäng mellan 0 och 1
        cosine_scores = util.cos_sim(embeddings, embeddings)

        # 4. Gruppera kopiorna
        duplicate_groups = []
        visited = set()

        for i in range(len(image_paths)):
            if i in visited:
                continue
            
            current_group = [image_paths[i]]
            for j in range(i + 1, len(image_paths)):
                if j not in visited and cosine_scores[i][j] > threshold:
                    current_group.append(image_paths[j])
                    visited.add(j)
            
            if len(current_group) > 1:
                duplicate_groups.append(current_group)
                visited.add(i)

        return duplicate_groups
    


if __name__ == "__main__":
# 1. Starta analysatorn
     print("Laddar AI-modell... (detta kan ta en stund första gången)")
analyzer = ImageAnalyzer()

   # 2. Ange sökväg till din testmapp
test_folder = "test_images" # Se till att denna mapp finns!

if not os.path.exists(test_folder):
       print(f"Hittade inte mappen: {test_folder}. Skapa den och lägg i några bilder.")
else:
       print(f"Analyserar bilder i: {test_folder}...")
        
       # 3. Kör analysen
       # Vi sätter threshold till 0.9 för att vara lite mer tillåtande
       groups = analyzer.find_duplicates(test_folder, threshold=0.9)

       # 4. Presentera resultatet
       if not groups:
           print("Inga kopior hittades.")
       else:
            print(f"\n--- Hittade {len(groups)} grupper av kopior ---")
            for i, group in enumerate(groups):
                print(f"\nGrupp {i+1}:")
                for path in group:
                    size = os.path.getsize(path) // 1024
                    print(f"  - {os.path.basename(path)} ({size} KB)")