import os
import cv2
import numpy as np
from uuid import uuid4

async def process_tryon_image(user_photo, clothing_photo):
    # Read user photo
    user_contents = await user_photo.read()
    user_np = np.frombuffer(user_contents, np.uint8)
    user_img = cv2.imdecode(user_np, cv2.IMREAD_COLOR)

    # Read clothing photo
    clothing_contents = await clothing_photo.read()
    clothing_np = np.frombuffer(clothing_contents, np.uint8)
    clothing_img = cv2.imdecode(clothing_np, cv2.IMREAD_UNCHANGED)

    # Resize clothing to match user photo size
    clothing_resized = cv2.resize(clothing_img, (user_img.shape[1], user_img.shape[0]))

    # Simple alpha blending if clothing has transparency
    if clothing_resized.shape[2] == 4:
        alpha = clothing_resized[:, :, 3] / 255.0
        for c in range(3):
            user_img[:, :, c] = alpha * clothing_resized[:, :, c] + (1 - alpha) * user_img[:, :, c]

    # Save output
    output_filename = f"output_{uuid4().hex}.png"
    output_path = f"temp/{output_filename}"

    os.makedirs("temp", exist_ok=True)
    cv2.imwrite(output_path, user_img)

    return output_path
