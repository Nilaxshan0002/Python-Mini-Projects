import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from streamlit_drawable_canvas import st_canvas

# Set page config to look like a professional SaaS app
st.set_page_config(
    page_title="Cleanup Pictures",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to style the UI to match the modern, clean look of cleanup.pictures
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #f9f9fb;
    }
    /* Top header */
    header {
        background-color: transparent !important;
    }
    /* Custom Button Styling */
    .stButton>button {
        background-color: #c3ff00; /* The neon green from the screenshot */
        color: #000;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #aee600;
        box-shadow: 0 4px 12px rgba(195, 255, 0, 0.4);
    }
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    /* Headings */
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        color: #111;
    }
    .subtitle {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)


def process_image(image, mask, brush_size):
    """
    Uses OpenCV's Inpainting algorithm (Telea) to remove the masked area
    and fill it with the surrounding background.
    """
    # Convert PIL images to OpenCV format (NumPy arrays)
    img_array = np.array(image.convert("RGB"))
    # OpenCV uses BGR
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    # Process the mask (Canvas returns RGBA, we need grayscale for the mask)
    mask_array = np.array(mask.convert("L"))
    
    # CRITICAL FIX: Resize the mask to match the original image exactly
    # The canvas shrinks the image for display, so the mask is smaller than the original.
    mask_resized = cv2.resize(mask_array, (img_bgr.shape[1], img_bgr.shape[0]))
    
    # Ensure the mask is strictly binary (0 or 255)
    _, mask_binary = cv2.threshold(mask_resized, 10, 255, cv2.THRESH_BINARY)
    
    # Dilate the mask slightly to ensure edges are covered smoothly
    kernel = np.ones((brush_size, brush_size), np.uint8)
    dilated_mask = cv2.dilate(mask_binary, kernel, iterations=1)
    
    # Apply the inpainting algorithm (cv2.INPAINT_TELEA or cv2.INPAINT_NS)
    # The '3' is the inpaint radius (how many neighbor pixels to use)
    result_bgr = cv2.inpaint(img_bgr, dilated_mask, 3, cv2.INPAINT_TELEA)
    
    # Convert back to RGB for PIL/Streamlit
    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(result_rgb)


# --- UI LAYOUT ---

# Header area
col_logo, col_links = st.columns([2, 3])
with col_logo:
    st.markdown("<h2>✨ cleanup.pictures</h2>", unsafe_allow_html=True)
with col_links:
    st.markdown("<p style='text-align: right; color: #666;'>Pricing · FAQ · API</p>", unsafe_allow_html=True)

st.markdown("<h1>Remove objects, people and defects in seconds</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Upload an image, brush over the object you want to remove, and let AI clean it up.</p>", unsafe_allow_html=True)

# Sidebar for Upload & Settings
with st.sidebar:
    st.header("Settings ⚙️")
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    
    st.markdown("---")
    st.subheader("Brush Settings 🖌️")
    brush_size = st.slider("Brush Size", min_value=1, max_value=50, value=15)
    st.info("💡 Tip: Use the canvas below to brush over the object you want to remove. The AI updates automatically.")

# Main Workspace
if uploaded_file is not None:
    # Load the uploaded image
    original_image = Image.open(uploaded_file)
    
    # Calculate canvas dimensions to match the image aspect ratio
    # We cap the max width to fit the screen nicely
    img_width, img_height = original_image.size
    max_width = 500
    scale = max_width / img_width
    canvas_width = int(img_width * scale)
    canvas_height = int(img_height * scale)
    
    # We use columns to create a split-view (Original vs Result)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Before / Edit")
        
        # The Drawable Canvas
        canvas_result = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)", # Semi-transparent red mask
            stroke_width=brush_size,
            stroke_color="rgba(255, 0, 0, 0.8)",
            background_image=original_image,
            height=canvas_height,
            width=canvas_width,
            drawing_mode="freedraw",
            key="canvas",
            return_image_data=True,
        )
        
    # Check if the user has drawn on the canvas
    if canvas_result.image_data is not None:
        # Convert the canvas RGBA data to a PIL Image to use as a mask
        mask_image = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
        
        # Check if the mask actually has drawings (alpha channel > 0 means something is drawn)
        if np.any(canvas_result.image_data[:, :, 3] > 0):
            
            with st.spinner("AI is cleaning up the image... 🪄"):
                # Process the image
                result_image = process_image(original_image, mask_image, brush_size)
                
                with col2:
                    st.markdown("### After")
                    st.image(result_image, use_column_width=True)
                    
                    # Add a download button
                    buf = io.BytesIO()
                    result_image.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="⬇️ Download Cleaned Image",
                        data=byte_im,
                        file_name="cleaned_image.png",
                        mime="image/png"
                    )
        else:
            with col2:
                st.info("Brush over the object on the left to see the magic happen here! ✨")
            
else:
    # Empty State
    st.info("👈 Please upload an image from the sidebar to get started.")