import os
from pathlib import Path

from PIL import Image
from sentence_transformers import SentenceTransformer, util


class ImageAnalyzer:
    def __init__(self, model_name='clip-ViT-B-32'):
        self.model = SentenceTransformer(model_name)
        self.image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')

    def _collect_image_paths(self, folder_path):
        folder = Path(folder_path)
        if not folder.exists():
            return []

        image_paths = []
        for root, _, files in os.walk(folder):
            for filename in files:
                if filename.lower().endswith(self.image_extensions):
                    image_paths.append(str(Path(root) / filename))

        return sorted(image_paths)

    def find_duplicates(self, folder_path, threshold=0.95):
        """
        Går igenom mappen, skapar embeddings och hittar likheter.
        """
        image_paths = self._collect_image_paths(folder_path)
        if not image_paths:
            return []

        images = []
        for path in image_paths:
            with Image.open(path) as img:
                images.append(img.convert("RGB"))

        embeddings = self.model.encode(images, convert_to_tensor=True, show_progress_bar=False)
        cosine_scores = util.cos_sim(embeddings, embeddings)

        duplicate_groups = []
        visited = set()

        for i in range(len(image_paths)):
            if i in visited:
                continue

            current_group = [image_paths[i]]
            for j in range(i + 1, len(image_paths)):
                if j not in visited and cosine_scores[i][j].item() > threshold:
                    current_group.append(image_paths[j])
                    visited.add(j)

            if len(current_group) > 1:
                duplicate_groups.append(current_group)
                visited.add(i)

        return duplicate_groups


if __name__ == "__main__":
    print("Laddar AI-modell... (detta kan ta en stund första gången)")
    analyzer = ImageAnalyzer()

    test_folder = "test_images"
    if not os.path.exists(test_folder):
        print(f"Hittade inte mappen: {test_folder}. Skapa den och lägg i några bilder.")
    else:
        print(f"Analyserar bilder i: {test_folder}...")
        groups = analyzer.find_duplicates(test_folder, threshold=0.9)

        if not groups:
            print("Inga kopior hittades.")
        else:
            print(f"\n--- Hittade {len(groups)} grupper av kopior ---")
            for i, group in enumerate(groups):
                print(f"\nGrupp {i + 1}:")
                for path in group:
                    size = os.path.getsize(path) // 1024
                    print(f"  - {os.path.basename(path)} ({size} KB)")