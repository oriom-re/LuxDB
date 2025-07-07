
"""
📄 PDF Generator Flow - Generuje manifesty PDF z wykorzystaniem bytów logicznych

Specjalizowany flow do generowania dokumentów PDF na podstawie intencji.
"""

import uuid
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from io import BytesIO

from ..beings.logical_being import LogicalBeing, LogicType, LogicalContext
from ..beings.intention_being import IntentionBeing


class PDFGeneratorFlow:
    """
    Flow do generowania dokumentów PDF z wykorzystaniem bytów logicznych
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        
        # Specjalizowane byty do generowania PDF
        self.content_architect = LogicalBeing(
            LogicType.CREATIVE,
            LogicalContext(
                domain="document_generation",
                specialization="content_architecture"
            )
        )
        
        self.design_specialist = LogicalBeing(
            LogicType.ARTISTIC,
            LogicalContext(
                domain="visual_design",
                specialization="pdf_layout"
            )
        )
        
        self.manifest_philosopher = LogicalBeing(
            LogicType.EMERGENT,
            LogicalContext(
                domain="philosophical_content",
                specialization="manifest_creation"
            )
        )
        
        # Dostępne szablony
        self.templates = {
            'manifest': self._create_manifest_template(),
            'technical_doc': self._create_technical_template(),
            'creative_brief': self._create_creative_template()
        }
        
        # Generowane dokumenty
        self.generated_documents: List[Dict[str, Any]] = []
        
    def generate_manifest_pdf(self, title: str, content_sections: Dict[str, str], 
                            style: str = "manifest") -> Dict[str, Any]:
        """
        Generuje manifest PDF na podstawie intencji
        
        Args:
            title: Tytuł manifestu
            content_sections: Sekcje treści
            style: Styl dokumentu
            
        Returns:
            Informacje o wygenerowanym dokumencie
        """
        generation_start = datetime.now()
        
        # Utwórz intencję generowania
        generation_intention = IntentionBeing({
            'duchowa': {
                'opis_intencji': f'Stwórz manifest PDF: {title}',
                'kontekst': f'Styl: {style}, Sekcje: {len(content_sections)}',
                'inspiracja': 'Manifestować wizję w formie dokumentu',
                'energia_duchowa': 95.0
            },
            'materialna': {
                'zadanie': 'pdf_generation',
                'wymagania': ['content_processing', 'visual_design', 'pdf_creation'],
                'oczekiwany_rezultat': f'Manifest PDF pt. "{title}"',
                'techniczne_detale': {
                    'format': 'PDF',
                    'style': style,
                    'sections': list(content_sections.keys())
                }
            },
            'metainfo': {
                'zrodlo': 'pdf_generator_flow',
                'tags': ['manifest', 'pdf', 'document_generation']
            }
        })
        
        try:
            # 1. Architektura treści przez content_architect
            content_structure = self.content_architect.process_intention(
                generation_intention, 
                {'sections': content_sections, 'style': style}
            )
            
            # 2. Design wizualny przez design_specialist
            visual_design = self.design_specialist.process_intention(
                generation_intention,
                {'content_structure': content_structure, 'template': self.templates.get(style)}
            )
            
            # 3. Filozoficzna walidacja przez manifest_philosopher
            philosophical_validation = self.manifest_philosopher.process_intention(
                generation_intention,
                {'content': content_sections, 'design': visual_design}
            )
            
            # 4. Generuj rzeczywisty PDF
            pdf_result = self._create_pdf_document(
                title, content_sections, content_structure, visual_design
            )
            
            generation_time = (datetime.now() - generation_start).total_seconds()
            
            document_info = {
                'id': str(uuid.uuid4()),
                'title': title,
                'style': style,
                'file_path': pdf_result['file_path'],
                'file_size': pdf_result['file_size'],
                'page_count': pdf_result['page_count'],
                'generation_time': generation_time,
                'content_structure': content_structure,
                'visual_design': visual_design,
                'philosophical_validation': philosophical_validation,
                'created_at': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            self.generated_documents.append(document_info)
            
            self.engine.logger.info(f"📄 Manifest PDF '{title}' wygenerowany w {generation_time:.2f}s")
            
            return document_info
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd generowania PDF: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'title': title,
                'generation_time': (datetime.now() - generation_start).total_seconds()
            }
    
    def generate_from_intention_text(self, intention_text: str) -> Dict[str, Any]:
        """
        Generuje manifest na podstawie tekstu intencji
        Przykład użycia dla zadania z manifestem "Nie oddamy nudy żadnego sektora"
        """
        
        # Parsuj tekst intencji
        parsed_content = self._parse_intention_text(intention_text)
        
        # Wyodrębnij tytuł
        title = parsed_content.get('title', 'Manifest Bez Tytułu')
        
        # Organizuj sekcje
        sections = parsed_content.get('sections', {})
        
        return self.generate_manifest_pdf(title, sections, 'manifest')
    
    def _parse_intention_text(self, text: str) -> Dict[str, Any]:
        """Parsuje tekst intencji i wyodrębnia strukturę"""
        lines = text.strip().split('\n')
        
        title = "Manifest"
        sections = {}
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Wykryj tytuł
            if line.startswith('🧭 TYTUŁ:') or line.startswith('TYTUŁ:'):
                title = line.split(':', 1)[1].strip().strip('"')
                continue
            
            # Wykryj sekcje numerowane
            if line[0].isdigit() and '. ' in line:
                # Zapisz poprzednią sekcję
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Rozpocznij nową sekcję
                current_section = line.split('. ', 1)[1]
                current_content = []
                continue
            
            # Dodaj zawartość do bieżącej sekcji
            if current_section:
                current_content.append(line)
        
        # Zapisz ostatnią sekcję
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return {
            'title': title,
            'sections': sections
        }
    
    def _create_pdf_document(self, title: str, sections: Dict[str, str], 
                           structure: Dict[str, Any], design: Dict[str, Any]) -> Dict[str, Any]:
        """Tworzy rzeczywisty dokument PDF"""
        
        # Symulacja tworzenia PDF (w rzeczywistej implementacji użyłby biblioteki jak reportlab)
        pdf_content = self._generate_pdf_content(title, sections, structure, design)
        
        # Ścieżka do pliku
        filename = f"manifest_{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join('generated_pdfs', filename)
        
        # Utwórz katalog jeśli nie istnieje
        os.makedirs('generated_pdfs', exist_ok=True)
        
        # Zapisz PDF (symulacja)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(pdf_content)
        
        file_size = len(pdf_content.encode('utf-8'))
        page_count = max(1, len(sections))
        
        return {
            'file_path': file_path,
            'file_size': file_size,
            'page_count': page_count,
            'content_preview': pdf_content[:200] + '...' if len(pdf_content) > 200 else pdf_content
        }
    
    def _generate_pdf_content(self, title: str, sections: Dict[str, str], 
                            structure: Dict[str, Any], design: Dict[str, Any]) -> str:
        """Generuje zawartość PDF jako tekst (symulacja)"""
        
        content = []
        content.append("=" * 80)
        content.append(f"  {title.upper()}")
        content.append("=" * 80)
        content.append("")
        content.append(f"Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"Styl: {design.get('processing_type', 'manifest')}")
        content.append("")
        content.append("-" * 80)
        content.append("")
        
        for i, (section_title, section_content) in enumerate(sections.items(), 1):
            content.append(f"{i}. {section_title.upper()}")
            content.append("")
            
            # Podziel treść na akapity
            paragraphs = section_content.split('\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    content.append(f"   {paragraph.strip()}")
            
            content.append("")
            content.append("-" * 40)
            content.append("")
        
        content.append("")
        content.append("Wygenerowane przez Astra LuxDB v2 - System Bytów Logicznych")
        content.append("🌟 Manifestacja intencji w formie dokumentu")
        
        return '\n'.join(content)
    
    def _create_manifest_template(self) -> Dict[str, Any]:
        """Tworzy szablon dla manifestów"""
        return {
            'name': 'manifest',
            'description': 'Szablon dla manifestów i deklaracji',
            'structure': {
                'header': {'height': 100, 'style': 'bold_centered'},
                'sections': {'spacing': 20, 'style': 'structured'},
                'footer': {'height': 50, 'style': 'signature'}
            },
            'typography': {
                'title_font': 'bold_large',
                'section_font': 'medium',
                'body_font': 'regular'
            },
            'colors': {
                'primary': '#1a1a1a',
                'accent': '#4a90e2',
                'background': '#ffffff'
            }
        }
    
    def _create_technical_template(self) -> Dict[str, Any]:
        """Tworzy szablon dla dokumentów technicznych"""
        return {
            'name': 'technical_doc',
            'description': 'Szablon dla dokumentacji technicznej',
            'structure': {
                'header': {'height': 80, 'style': 'minimal'},
                'sections': {'spacing': 15, 'style': 'numbered'},
                'footer': {'height': 40, 'style': 'page_numbers'}
            },
            'typography': {
                'title_font': 'bold_medium',
                'section_font': 'medium',
                'body_font': 'small'
            },
            'colors': {
                'primary': '#333333',
                'accent': '#0066cc',
                'background': '#fafafa'
            }
        }
    
    def _create_creative_template(self) -> Dict[str, Any]:
        """Tworzy szablon dla dokumentów kreatywnych"""
        return {
            'name': 'creative_brief',
            'description': 'Szablon dla briefów kreatywnych',
            'structure': {
                'header': {'height': 120, 'style': 'artistic'},
                'sections': {'spacing': 25, 'style': 'flowing'},
                'footer': {'height': 60, 'style': 'creative_signature'}
            },
            'typography': {
                'title_font': 'artistic_large',
                'section_font': 'creative_medium',
                'body_font': 'flowing'
            },
            'colors': {
                'primary': '#2c3e50',
                'accent': '#e74c3c',
                'background': '#ecf0f1'
            }
        }
    
    def list_generated_documents(self) -> List[Dict[str, Any]]:
        """Zwraca listę wygenerowanych dokumentów"""
        return [
            {
                'id': doc['id'],
                'title': doc['title'],
                'style': doc['style'],
                'file_path': doc['file_path'],
                'page_count': doc['page_count'],
                'created_at': doc['created_at'],
                'status': doc['status']
            }
            for doc in self.generated_documents
        ]
    
    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera informacje o dokumencie"""
        for doc in self.generated_documents:
            if doc['id'] == document_id:
                return doc
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status PDF Generator Flow"""
        return {
            'type': 'pdf_generator_flow',
            'generated_documents_count': len(self.generated_documents),
            'available_templates': list(self.templates.keys()),
            'logical_beings': {
                'content_architect': self.content_architect.get_status()['logical_being_specific'],
                'design_specialist': self.design_specialist.get_status()['logical_being_specific'],
                'manifest_philosopher': self.manifest_philosopher.get_status()['logical_being_specific']
            },
            'recent_documents': [
                {
                    'title': doc['title'],
                    'created_at': doc['created_at'],
                    'status': doc['status']
                }
                for doc in self.generated_documents[-5:]
            ]
        }
