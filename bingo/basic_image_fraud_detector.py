from PIL import Image
import io
from django.core.cache import cache
import logging
import math

logger = logging.getLogger(__name__)


class BasicImageFraudDetector:
    """
    A simple image fraud detector that uses only PIL.
    This avoids the need for complex dependencies like OpenCV and ImageHash.
    """

    def __init__(self, similarity_threshold=85):
        """
        Initialize the fraud detector with a similarity threshold.

        Args:
            similarity_threshold (int): Percentage similarity above which images are considered duplicates.
        """
        self.similarity_threshold = similarity_threshold

    def _get_image_signature(self, image_data):
        """
        Create a simple image signature using downsampling and average pixel values.

        Args:
            image_data: Binary image data

        Returns:
            dict: Dictionary containing image signature
        """
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))

            # Convert to grayscale
            gray_image = image.convert('L')

            # Resize to small dimensions (16x16) for a basic perceptual hash
            small_image = gray_image.resize((16, 16), Image.LANCZOS)

            # Get pixel data
            pixels = list(small_image.getdata())

            # Calculate average pixel value
            avg_pixel = sum(pixels) / len(pixels)

            # Create a simple binary hash (1 for pixels above average, 0 for below)
            binary_hash = ''.join('1' if p > avg_pixel else '0' for p in pixels)

            # Get basic image stats
            width, height = image.size
            aspect_ratio = width / height

            # Get sample pixels from different regions (simplified color analysis)
            regions = []
            for x in [0.25, 0.5, 0.75]:
                for y in [0.25, 0.5, 0.75]:
                    px = int(width * x)
                    py = int(height * y)
                    if image.mode == 'RGB':
                        regions.append(image.getpixel((px, py)))
                    else:
                        # Convert to RGB if not already
                        regions.append(image.convert('RGB').getpixel((px, py)))

            return {
                'binary_hash': binary_hash,
                'size': f"{width}x{height}",
                'aspect_ratio': aspect_ratio,
                'regions': regions
            }
        except Exception as e:
            logger.error(f"Error calculating image signature: {str(e)}")
            return None

    def _calculate_hash_similarity(self, hash1, hash2):
        """
        Calculate similarity between two binary hash strings.

        Args:
            hash1 (str): First hash string
            hash2 (str): Second hash string

        Returns:
            float: Similarity percentage (0-100)
        """
        if len(hash1) != len(hash2):
            return 0

        matching_bits = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
        similarity = (matching_bits / len(hash1)) * 100
        return similarity

    def _calculate_color_similarity(self, regions1, regions2):
        """
        Calculate color similarity between two sets of region samples.

        Args:
            regions1: List of RGB tuples from first image
            regions2: List of RGB tuples from second image

        Returns:
            float: Color similarity percentage (0-100)
        """
        if len(regions1) != len(regions2):
            return 0

        total_diff = 0
        max_possible_diff = 255 * 3 * len(regions1)  # 3 channels, 255 max diff per channel, per region

        for (r1, g1, b1), (r2, g2, b2) in zip(regions1, regions2):
            # Calculate Euclidean distance in RGB space
            diff = math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)
            total_diff += diff

        # Convert to a similarity percentage (0-100)
        similarity = 100 - (total_diff / max_possible_diff) * 100
        return max(0, similarity)

    def is_image_fraudulent(self, new_image_data, user_id=None):
        """
        Check if an image is potentially fraudulent by comparing it to previously approved images.

        Args:
            new_image_data: Binary image data of the new submission
            user_id: Optional user ID to check only against this user's submissions

        Returns:
            tuple: (is_fraudulent, similarity_percentage, matched_task_id)
        """
        print("=== FRAUD DETECTION STARTED ===")

        # Calculate signature for the new image
        new_signature = self._get_image_signature(new_image_data)
        if not new_signature:
            logger.error("Could not calculate signature for new image")
            return False, 0, None

        print(f"New image size: {len(new_image_data)} bytes")
        print(f"New image signature calculated: {new_signature['binary_hash'][:20]}...")

        # Get previously approved images
        from .models import UserTask

        # Get all tasks with photos (including approved and pending)
        # We want to check for duplicates in any status to prevent multiple submissions of the same image
        query = UserTask.objects.exclude(photo='')

        # If user_id provided, check only against this user's previous uploads
        if user_id:
            query = query.filter(user_id=user_id)

        previous_tasks = query.order_by('-completion_date')[:30]
        print(f"Found {len(previous_tasks)} previous tasks to compare against")

        highest_similarity = 0
        matched_task_id = None

        for task in previous_tasks:
            try:
                print(f"Comparing with task #{task.id}...")

                # Get image data - handle Django's file field properly
                try:
                    # Make sure the file is open for reading
                    task.photo.open('rb')
                    previous_image_data = task.photo.read()
                    task.photo.close()
                except Exception as file_error:
                    print(f"Error reading photo for task #{task.id}: {str(file_error)}")
                    continue

                print(f"Previous image size: {len(previous_image_data)} bytes")

                # Calculate signature for previous image
                prev_signature = self._get_image_signature(previous_image_data)

                if not prev_signature:
                    print(f"Could not calculate signature for task #{task.id}")
                    continue

                print(f"Previous signature: {prev_signature['binary_hash'][:20]}...")

                # Compare binary hashes
                hash_similarity = self._calculate_hash_similarity(
                    new_signature['binary_hash'],
                    prev_signature['binary_hash']
                )

                # Compare color samples
                color_similarity = self._calculate_color_similarity(
                    new_signature['regions'],
                    prev_signature['regions']
                )

                print(f"Hash similarity: {hash_similarity:.2f}%, Color similarity: {color_similarity:.2f}%")

                # Use max similarity instead of weighted average for stricter detection
                final_similarity = max(hash_similarity, color_similarity)

                print(f"Final similarity: {final_similarity:.2f}%")

                if final_similarity > highest_similarity:
                    highest_similarity = final_similarity
                    matched_task_id = task.id
                    print(f"New highest similarity: {highest_similarity:.2f}% with task #{matched_task_id}")

                # Early exit if we find a very high match
                if highest_similarity > 95:
                    print(f"Found very high similarity ({highest_similarity:.2f}%), stopping search")
                    break

            except Exception as e:
                logger.error(f"Error comparing with task {task.id}: {str(e)}")
                print(f"Error comparing with task {task.id}: {str(e)}")
                continue

        # Lower threshold for stricter detection
        similarity_threshold = self.similarity_threshold
        print(f"Highest similarity found: {highest_similarity:.2f}%, threshold: {similarity_threshold}")

        # Determine if fraudulent based on similarity threshold
        is_fraudulent = highest_similarity >= similarity_threshold

        print(f"Image is {'fraudulent' if is_fraudulent else 'legitimate'}")
        print("=== FRAUD DETECTION COMPLETED ===")

        return is_fraudulent, highest_similarity, matched_task_id

    def save_image_signature(self, task_id, image_data):
        """
        Save image signature for a newly approved image.

        Args:
            task_id: The ID of the approved task
            image_data: Binary image data
        """
        signature = self._get_image_signature(image_data)
        if signature:
            # Store in cache for quick access
            cache_key = f"image_signature_{task_id}"
            cache.set(cache_key, signature, timeout=60 * 60 * 24 * 30)  # Store for 30 days