# app/scripts/analyze_service.py
"""
Servicio de análisis optimizado - Extrae lógica del script original
Procesa 1 imagen a la vez con máximo rendimiento
YOLO (detección) → SAM (segmentación) → ResNet (clasificación)
"""

import os
import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from datetime import datetime
from torchvision import transforms, models
from ultralytics import YOLO
import base64
import urllib.request
from pathlib import Path


class AnalysisService:
    """Servicio para analizar imágenes con pipeline optimizado"""
    
    def __init__(self, config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Cargar modelos
        self._load_yolo()
        self._load_classifier()
        self._load_sam()
        
        print(f"[INFO] Modelos cargados. Device: {self.device}")
    
    def _load_yolo(self):
        """Carga YOLO exacto como el original"""
        yolo_path = self.config['YOLO']['weights']
        if not os.path.exists(yolo_path):
            raise FileNotFoundError(f"Modelo YOLO no encontrado: {yolo_path}")
        
        self.yolo = YOLO(yolo_path)
        print(f"[YOLO] Cargado desde {yolo_path}")
    
    def _load_classifier(self):
        """Carga ResNet exacto como el original"""
        clf_path = self.config['RESNET']['weights']
        if not os.path.exists(clf_path):
            raise FileNotFoundError(f"Modelo clasificador no encontrado: {clf_path}")
        
        # Cargar checkpoint - IGUAL AL ORIGINAL
        ckpt = torch.load(clf_path, map_location=self.device)
        self.class_names = ckpt.get("classes", ["healthy", "affected"])
        args = ckpt.get("args", {})
        model_name = str(args.get("model", "resnet18")).lower()
        
        # Crear modelo - IGUAL AL ORIGINAL
        if model_name == "resnet50":
            model = models.resnet50(weights=None)
            in_feats = model.fc.in_features
            model.fc = nn.Linear(in_feats, len(self.class_names))
        else:
            model = models.resnet18(weights=None)
            in_feats = model.fc.in_features
            model.fc = nn.Linear(in_feats, len(self.class_names))
        
        # Cargar pesos - IGUAL AL ORIGINAL
        state = ckpt.get("state_dict", ckpt)
        model.load_state_dict(state)
        model.to(self.device).eval()
        self.classifier = model
        
        # Transform - IGUAL AL ORIGINAL
        img_size = int(args.get("img_size", 384))
        mean = [0.485, 0.456, 0.406]
        std = [0.229, 0.224, 0.225]
        self.clf_transform = transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
        ])
        
        print(f"[CLASSIFIER] ResNet cargado. Clases: {self.class_names}")
    
    def _load_sam(self):
        """Carga SAM como el original"""
        # CAMBIO IMPORTANTE: Eliminar la importación problemática
        sam_mode = self.config.get('SAM_MODE', 'off')
        if sam_mode == 'off':
            self.sam = None
            self.mask_generator = None
            print("[SAM] Deshabilitado")
            return
        
        try:
            from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
            
            sam_path = self.config['SAM']['checkpoint']
            
            # Descargar si no existe - COMO EL ORIGINAL
            if not os.path.exists(sam_path):
                self._download_sam_checkpoint(sam_path)
            
            model_type = self.config['SAM']['model']
            self.sam = sam_model_registry[model_type](checkpoint=sam_path).to(self.device)
            
            # Build mask generator - COMO EL ORIGINAL
            sam_config = self.config['SAM']
            H, W = 960, 960  # Dimensión típica
            min_area = int(sam_config.get('min_area_frac', 0.10) * (H * W))
            
            self.mask_generator = SamAutomaticMaskGenerator(
                model=self.sam,
                points_per_side=sam_config.get('points_per_side', 16),  # Como original
                pred_iou_thresh=sam_config.get('pred_iou_thresh', 0.90),
                stability_score_thresh=sam_config.get('stability_score_thresh', 0.95),
                crop_n_layers=0,
                crop_n_points_downscale_factor=2,
                min_mask_region_area=min_area,
            )
            
            print(f"[SAM] {model_type} cargado desde {sam_path}")
        except Exception as e:
            print(f"[SAM] Error cargando: {e}")
            self.sam = None
            self.mask_generator = None
    
    def _download_sam_checkpoint(self, checkpoint_path):
        """Descarga checkpoint SAM si no existe"""
        SAM_URLS = {
            "vit_b": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
            "vit_l": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth",
            "vit_h": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
        }
        
        model_type = self.config['SAM']['model']
        url = SAM_URLS.get(model_type)
        
        if not url:
            raise ValueError(f"No hay URL para SAM '{model_type}'")
        
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        print(f"[SAM] Descargando {model_type}...")
        urllib.request.urlretrieve(url, checkpoint_path)
        print(f"[SAM] Descargado en {checkpoint_path}")
    
    def analyze_image(self, image_path: str) -> dict:
        """Analiza 1 imagen - PIPELINE OPTIMIZADO"""
        
        # Leer imagen
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"No se pudo leer: {image_path}")
        
        img_h, img_w = img.shape[:2]
        print(f"[ANALYZE] Imagen: {img_w}x{img_h}")
        
        # PASO 1: Detección YOLO
        print("[ANALYZE] Detectando con YOLO...")
        detections = self._detect_yolo(img)
        
        if not detections:
            return self._empty_result()
        
        print(f"[ANALYZE] {len(detections)} hojas detectadas")
        
        # PASO 2: Clasificación (con SAM opcional)
        print("[ANALYZE] Clasificando hojas...")
        results = self._classify_all(img, detections)
        
        # PASO 3: Dibujar y procesar
        processed_img = self._draw_results(img.copy(), results)
        img_base64 = self._image_to_base64(processed_img)
        
        # Contar
        healthy = sum(1 for r in results if r['class'] == 'healthy')
        affected = sum(1 for r in results if r['class'] == 'affected')
        confidence = np.mean([r['score'] for r in results]) * 100 if results else 0.0
        
        print(f"[ANALYZE] ✓ Resultado: {healthy} sanas, {affected} afectadas")
        
        return {
            'total_leaves': len(results),
            'healthy_leaves': healthy,
            'affected_leaves': affected,
            'confidence': float(confidence),
            'processed_image_base64': img_base64,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def _detect_yolo(self, img):
        """Detección YOLO - COMO EL ORIGINAL"""
        
        conf = self.config['YOLO']['conf']
        imgsz = self.config['YOLO']['imgsz']
        iou = self.config['YOLO'].get('iou', 0.45)
        
        # Inferencia - EXACTO AL ORIGINAL
        results = self.yolo(
            img,
            conf=conf,
            imgsz=imgsz,
            iou=iou,
            device=self.device,
            verbose=False
        )
        
        detections = []
        if results and results[0].boxes is not None:
            for box in results[0].boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf_score = float(box.conf[0])
                detections.append({
                    'xyxy': (x1, y1, x2, y2),
                    'conf': conf_score,
                })
        
        return detections
    
    def _classify_all(self, img, detections):
        """Clasifica todas las detecciones"""
        
        results = []
        for i, det in enumerate(detections):
            result = self._classify_one(img, det)
            if result:
                results.append(result)
                print(f"  [{i+1}/{len(detections)}] {result['class'].upper()} ({result['score']:.3f})")
        
        return results
    
    def _classify_one(self, img, det):
        """Clasifica UNA detección - CORE LOGIC"""
        
        x1, y1, x2, y2 = det['xyxy']
        
        # Recortar región
        crop = img[int(y1):int(y2), int(x1):int(x2)]
        if crop.size == 0:
            return None
        
        # SAM: Segmentar si está habilitado
        if self.sam and self.mask_generator:
            try:
                masks = self.mask_generator.generate(crop)
                if masks:
                    # Tomar máscara más grande - COMO EL ORIGINAL
                    best_mask = max(masks, key=lambda m: m.get('area', 0))
                    mask_bool = best_mask['segmentation']
                    crop = self._apply_mask_to_crop(crop, mask_bool)
            except Exception as e:
                print(f"    [SAM Error] {e}")
        
        # Clasificar con ResNet - EXACTO AL ORIGINAL
        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(crop_rgb)
        
        x = self.clf_transform(pil_img).unsqueeze(0).to(self.device)
        with torch.inference_mode():
            logits = self.classifier(x)
            probs = torch.softmax(logits, dim=1)[0]
        
        pred_idx = torch.argmax(probs)
        pred_score = float(probs[pred_idx])
        pred_class = self.class_names[pred_idx]
        
        return {
            'xyxy': det['xyxy'],
            'class': pred_class,
            'score': pred_score,
            'conf': det['conf'],
        }
    
    def _apply_mask_to_crop(self, crop, mask_bool):
        """Aplica máscara SAM"""
        
        mask_uint8 = (mask_bool > 0).astype(np.uint8) * 255
        
        # Limpiar máscara - COMO EL ORIGINAL
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask_uint8 = cv2.morphologyEx(mask_uint8, cv2.MORPH_OPEN, kernel, iterations=1)
        mask_uint8 = cv2.morphologyEx(mask_uint8, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Obtener bounding box
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return crop
        
        x, y, w, h = cv2.boundingRect(np.vstack(contours))
        x1 = max(0, x - 5)
        y1 = max(0, y - 5)
        x2 = min(crop.shape[1], x + w + 5)
        y2 = min(crop.shape[0], y + h + 5)
        
        return crop[y1:y2, x1:x2]
    
    def _draw_results(self, img, results):
        """Dibuja cajas y etiquetas"""
        
        for res in results:
            x1, y1, x2, y2 = res['xyxy']
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Color y etiqueta
            if res['class'] == 'healthy':
                color = (0, 255, 0)  # Verde
                label = f"Sana ({res['score']:.2f})"
            else:
                color = (0, 0, 255)  # Rojo
                label = f"Afectada ({res['score']:.2f})"
            
            # Dibujar caja
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            
            # Dibujar texto
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1
            text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
            
            text_x = x1
            text_y = max(y1 - 5, text_size[1])
            
            cv2.rectangle(img, (text_x, text_y - text_size[1] - 3),
                         (text_x + text_size[0], text_y + 3), color, -1)
            cv2.putText(img, label, (text_x, text_y),
                       font, font_scale, (255, 255, 255), thickness)
        
        return img
    
    def _image_to_base64(self, img):
        """Convierte a base64"""
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
        return f"data:image/jpeg;base64,{img_base64}"
    
    def _empty_result(self):
        """Resultado vacío"""
        return {
            'total_leaves': 0,
            'healthy_leaves': 0,
            'affected_leaves': 0,
            'confidence': 0.0,
            'processed_image_base64': '',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


def create_analysis_service(config):
    return AnalysisService(config)