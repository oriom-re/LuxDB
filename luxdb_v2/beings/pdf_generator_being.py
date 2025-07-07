
"""
📄 PDFGeneratorBeing - Żywy Byt Generacji PDF

Zastępuje martwe flows żywym bytem z własną inteligencją i adaptacją.
Posiada specjalistyczną wiedzę o tworzeniu dokumentów PDF.
"""

import uuid
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from .logical_being import LogicalBeing, LogicType, LogicalContext, MicroFunction
from .intention_being import IntentionBeing


@dataclass
class DocumentStyle:
    """Styl dokumentu PDF"""
    name: str
    description: str
    colors: Dict[str, str] = field(default_factory=dict)
    fonts: Dict[str, str] = field(default_factory=dict)
    layout: Dict[str, Any] = field(default_factory=dict)
    templates: Dict[str, str] = field(default_factory=dict)


@dataclass
class GenerationTask:
    """Zadanie generowania PDF"""
    task_id: str
    title: str
    content: Dict[str, Any]
    style: str
    priority: int = 2
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    progress: float = 0.0
    output_path: Optional[str] = None
    generation_time: Optional[float] = None
    error_message: Optional[str] = None


class PDFGeneratorBeing(LogicalBeing):
    """
    Żywy byt specjalizujący się w generowaniu PDF
    Posiada własną inteligencję i zdolność adaptacji
    """
    
    def __init__(self, realm=None):
        context = LogicalContext(
            domain="document_generation",
            specialization="pdf_creation_and_design",
            knowledge_base={
                'supported_formats': ['manifest', 'technical_doc', 'creative_brief', 'report'],
                'layout_principles': ['harmony', 'readability', 'visual_hierarchy'],
                'design_patterns': ['minimalist', 'professional', 'artistic', 'technical']
            },
            patterns=['title_page', 'table_of_contents', 'sections', 'footer']
        )
        
        super().__init__(LogicType.CREATIVE, context, realm)
        
        # Specjalistyczne właściwości
        self.document_styles: Dict[str, DocumentStyle] = {}
        self.generation_queue: List[GenerationTask] = []
        self.completed_documents: List[Dict[str, Any]] = []
        self.template_library: Dict[str, str] = {}
        
        # Statystyki
        self.total_generated = 0
        self.successful_generations = 0
        self.average_generation_time = 0.0
        
        self.essence.name = "PDFGeneratorBeing"
        
        # Inicjalizuj style i mikro-funkcje
        self._initialize_document_styles()
        self._create_specialized_micro_functions()
    
    def _initialize_document_styles(self):
        """Inicjalizuje dostępne style dokumentów"""
        
        # Styl Manifest
        manifest_style = DocumentStyle(
            name="manifest",
            description="Styl dla manifestów i deklaracji duchowych",
            colors={
                'primary': '#1a1a1a',
                'accent': '#4a90e2',
                'background': '#ffffff',
                'highlight': '#f8f9fa'
            },
            fonts={
                'title': 'bold_large',
                'section': 'medium_bold',
                'body': 'regular',
                'quote': 'italic'
            },
            layout={
                'page_margins': {'top': 40, 'bottom': 40, 'left': 30, 'right': 30},
                'section_spacing': 25,
                'line_height': 1.6,
                'title_alignment': 'center'
            },
            templates={
                'header': '✨ {title} ✨',
                'section': '{number}. {title}',
                'footer': 'Wygenerowane przez Astra LuxDB v2 - {timestamp}'
            }
        )
        
        # Styl Techniczny
        technical_style = DocumentStyle(
            name="technical",
            description="Styl dla dokumentacji technicznej",
            colors={
                'primary': '#333333',
                'accent': '#0066cc',
                'background': '#fafafa',
                'code_bg': '#f4f4f4'
            },
            fonts={
                'title': 'bold_medium',
                'section': 'medium',
                'body': 'small',
                'code': 'monospace'
            },
            layout={
                'page_margins': {'top': 30, 'bottom': 30, 'left': 25, 'right': 25},
                'section_spacing': 15,
                'line_height': 1.4,
                'title_alignment': 'left'
            },
            templates={
                'header': '{title} | Dokumentacja Techniczna',
                'section': '{number}. {title}',
                'footer': 'Strona {page} | {timestamp}'
            }
        )
        
        # Styl Kreatywny
        creative_style = DocumentStyle(
            name="creative",
            description="Styl dla dokumentów kreatywnych",
            colors={
                'primary': '#2c3e50',
                'accent': '#e74c3c',
                'background': '#ecf0f1',
                'artistic': '#9b59b6'
            },
            fonts={
                'title': 'artistic_large',
                'section': 'creative_medium',
                'body': 'flowing',
                'emphasis': 'bold_italic'
            },
            layout={
                'page_margins': {'top': 50, 'bottom': 50, 'left': 40, 'right': 40},
                'section_spacing': 30,
                'line_height': 1.8,
                'title_alignment': 'center'
            },
            templates={
                'header': '🎨 {title} 🎨',
                'section': '• {title} •',
                'footer': '✨ Twórczość bez granic ✨'
            }
        )
        
        self.document_styles.update({
            'manifest': manifest_style,
            'technical': technical_style,
            'creative': creative_style
        })
    
    def _create_specialized_micro_functions(self):
        """Tworzy specjalistyczne mikro-funkcje dla generowania PDF"""
        
        # Funkcja parsowania tekstu intencji
        parse_intention_code = """
def parse_intention_text(text):
    lines = text.strip().split('\\n')
    title = "Dokument"
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
            if current_section and current_content:
                sections[current_section] = '\\n'.join(current_content)
            
            current_section = line.split('. ', 1)[1]
            current_content = []
            continue
        
        if current_section:
            current_content.append(line)
    
    if current_section and current_content:
        sections[current_section] = '\\n'.join(current_content)
    
    result = {'title': title, 'sections': sections}
"""
        
        parse_function = self.create_micro_function(
            name="parse_intention_text",
            language="python",
            code=parse_intention_code,
            purpose="Parsuje tekst intencji i wyodrębnia strukturę dokumentu"
        )
        
        # Funkcja generowania zawartości
        content_generation_code = """
def generate_pdf_content(title, sections, style_config):
    content = []
    
    # Header z dekoracją
    if style_config.get('name') == 'manifest':
        content.append("=" * 80)
        content.append(f"  ✨ {title.upper()} ✨")
        content.append("=" * 80)
    else:
        content.append(f"{title}")
        content.append("-" * len(title))
    
    content.append("")
    content.append(f"Wygenerowano: {args[3] if len(args) > 3 else 'teraz'}")
    content.append("")
    
    # Sekcje
    for i, (section_title, section_content) in enumerate(sections.items(), 1):
        content.append(f"{i}. {section_title.upper()}")
        content.append("")
        
        paragraphs = section_content.split('\\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                content.append(f"   {paragraph.strip()}")
        
        content.append("")
        content.append("-" * 40)
        content.append("")
    
    # Footer
    content.append("🌟 Wygenerowane przez PDFGeneratorBeing - Żywy System Tworzenia Dokumentów")
    
    result = '\\n'.join(content)
"""
        
        self.create_micro_function(
            name="generate_pdf_content",
            language="python", 
            code=content_generation_code,
            purpose="Generuje zawartość PDF zgodną ze stylem"
        )
        
        # Funkcja optymalizacji layoutu
        layout_optimization_code = """
def optimize_layout(content, style_config):
    # Oblicz optymalne rozmiary
    estimated_pages = max(1, len(content.split('\\n')) // 50)
    
    # Dostosuj marginesy
    margins = style_config.get('layout', {}).get('page_margins', {})
    optimized_margins = {
        'top': margins.get('top', 30),
        'bottom': margins.get('bottom', 30),
        'left': margins.get('left', 25),
        'right': margins.get('right', 25)
    }
    
    # Dostosuj spacing
    section_spacing = style_config.get('layout', {}).get('section_spacing', 20)
    
    result = {
        'estimated_pages': estimated_pages,
        'optimized_margins': optimized_margins,
        'section_spacing': section_spacing,
        'optimization_applied': True
    }
"""
        
        self.create_micro_function(
            name="optimize_layout",
            language="python",
            code=layout_optimization_code,
            purpose="Optymalizuje layout dokumentu dla lepszej czytelności"
        )
    
    def process_intention(self, intention: IntentionBeing, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Przetwarza intencję generowania PDF przez własną inteligencję
        """
        understanding = self._analyze_intention_understanding(intention, context)
        
        if understanding['level'].value < 2:  # Poniżej INTERMEDIATE
            return self._request_clarification(intention, understanding)
        
        # Wyodrębnij typ dokumentu z intencji
        doc_type = self._determine_document_type(intention)
        
        # Sprawdź czy mamy odpowiedni styl
        if doc_type not in self.document_styles:
            doc_type = 'manifest'  # domyślny
        
        try:
            # Utwórz zadanie generowania
            task = self._create_generation_task(intention, doc_type)
            
            # Dodaj do kolejki
            self.generation_queue.append(task)
            
            # Rozpocznij generowanie
            result = self._execute_generation(task)
            
            # Zapisz statystyki
            self._update_generation_statistics(result)
            
            return {
                'status': 'pdf_generation_completed' if result['success'] else 'pdf_generation_failed',
                'task_id': task.task_id,
                'document_info': result,
                'processing_type': 'pdf_generation',
                'being_type': 'specialized_pdf_generator'
            }
            
        except Exception as e:
            return {
                'status': 'pdf_generation_error',
                'error': str(e),
                'processing_type': 'pdf_generation',
                'being_type': 'specialized_pdf_generator'
            }
    
    def _determine_document_type(self, intention: IntentionBeing) -> str:
        """Określa typ dokumentu na podstawie intencji"""
        
        # Sprawdź tagi
        tags = intention.metainfo.tags
        if 'manifest' in tags:
            return 'manifest'
        elif 'technical' in tags or 'documentation' in tags:
            return 'technical'
        elif 'creative' in tags or 'artistic' in tags:
            return 'creative'
        
        # Sprawdź treść
        content = intention.duchowa.opis_intencji.lower()
        if 'manifest' in content or 'nie oddamy' in content:
            return 'manifest'
        elif 'dokumentacja' in content or 'technical' in content:
            return 'technical'
        elif 'kreatywn' in content or 'artystyczn' in content:
            return 'creative'
        
        return 'manifest'  # domyślny
    
    def _create_generation_task(self, intention: IntentionBeing, doc_type: str) -> GenerationTask:
        """Tworzy zadanie generowania"""
        
        task = GenerationTask(
            task_id=str(uuid.uuid4()),
            title=intention.essence.name,
            content={
                'intention_text': intention.duchowa.opis_intencji,
                'material_task': intention.materialna.zadanie,
                'requirements': intention.materialna.wymagania,
                'expected_result': intention.materialna.oczekiwany_rezultat
            },
            style=doc_type,
            priority=intention.priority.value
        )
        
        return task
    
    def _execute_generation(self, task: GenerationTask) -> Dict[str, Any]:
        """Wykonuje generowanie PDF"""
        start_time = datetime.now()
        
        try:
            task.status = "processing"
            task.progress = 10.0
            
            # 1. Parsuj treść przez mikro-funkcję
            if 'parse_intention_text' in self.micro_functions:
                parsed_content = self.execute_micro_function(
                    'parse_intention_text',
                    task.content.get('intention_text', '')
                )
            else:
                parsed_content = {
                    'title': task.title,
                    'sections': {'Główna sekcja': task.content.get('intention_text', '')}
                }
            
            task.progress = 30.0
            
            # 2. Wybierz styl
            style_config = self.document_styles[task.style]
            
            task.progress = 50.0
            
            # 3. Generuj zawartość przez mikro-funkcję
            if 'generate_pdf_content' in self.micro_functions:
                pdf_content = self.execute_micro_function(
                    'generate_pdf_content',
                    parsed_content['title'],
                    parsed_content['sections'],
                    style_config.__dict__,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            else:
                pdf_content = self._fallback_content_generation(parsed_content, style_config)
            
            task.progress = 70.0
            
            # 4. Optymalizuj layout
            if 'optimize_layout' in self.micro_functions:
                layout_info = self.execute_micro_function(
                    'optimize_layout',
                    pdf_content,
                    style_config.__dict__
                )
            else:
                layout_info = {'estimated_pages': 1, 'optimization_applied': False}
            
            task.progress = 90.0
            
            # 5. Zapisz plik
            filename = f"{task.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = os.path.join('generated_pdfs', filename)
            
            # Utwórz katalog jeśli nie istnieje
            os.makedirs('generated_pdfs', exist_ok=True)
            
            # Zapisz jako tekst (symulacja PDF)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(pdf_content)
            
            task.progress = 100.0
            task.status = "completed"
            task.output_path = output_path
            
            generation_time = (datetime.now() - start_time).total_seconds()
            task.generation_time = generation_time
            
            # Dodaj do ukończonych
            document_info = {
                'task_id': task.task_id,
                'title': task.title,
                'style': task.style,
                'file_path': output_path,
                'file_size': len(pdf_content.encode('utf-8')),
                'page_count': layout_info.get('estimated_pages', 1),
                'generation_time': generation_time,
                'created_at': datetime.now().isoformat(),
                'success': True
            }
            
            self.completed_documents.append(document_info)
            
            self.remember('pdf_generated', {
                'task_id': task.task_id,
                'title': task.title,
                'style': task.style,
                'success': True,
                'generation_time': generation_time
            })
            
            return document_info
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            
            return {
                'task_id': task.task_id,
                'success': False,
                'error': str(e),
                'generation_time': (datetime.now() - start_time).total_seconds()
            }
    
    def _fallback_content_generation(self, parsed_content: Dict[str, Any], style_config: DocumentStyle) -> str:
        """Fallback generowanie zawartości gdy mikro-funkcje nie działają"""
        content = []
        
        title = parsed_content.get('title', 'Dokument')
        sections = parsed_content.get('sections', {})
        
        # Header
        content.append("=" * 80)
        content.append(f"  {title.upper()}")
        content.append("=" * 80)
        content.append("")
        content.append(f"Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"Styl: {style_config.name}")
        content.append("")
        
        # Sekcje
        for i, (section_title, section_content) in enumerate(sections.items(), 1):
            content.append(f"{i}. {section_title.upper()}")
            content.append("")
            
            paragraphs = section_content.split('\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    content.append(f"   {paragraph.strip()}")
            
            content.append("")
            content.append("-" * 40)
            content.append("")
        
        content.append("🌟 Wygenerowane przez PDFGeneratorBeing")
        
        return '\n'.join(content)
    
    def _update_generation_statistics(self, result: Dict[str, Any]):
        """Aktualizuje statystyki generowania"""
        self.total_generated += 1
        
        if result.get('success', False):
            self.successful_generations += 1
            
            # Aktualizuj średni czas generowania
            gen_time = result.get('generation_time', 0)
            if self.average_generation_time == 0:
                self.average_generation_time = gen_time
            else:
                self.average_generation_time = (self.average_generation_time + gen_time) / 2
    
    def generate_from_text(self, text: str, style: str = "manifest", title: str = None) -> Dict[str, Any]:
        """
        Bezpośrednie generowanie PDF z tekstu
        """
        # Stwórz pseudo-intencję
        intention_data = {
            'duchowa': {
                'opis_intencji': text,
                'energia_duchowa': 100.0
            },
            'materialna': {
                'zadanie': 'pdf_generation',
                'wymagania': ['text_parsing', 'content_generation'],
                'oczekiwany_rezultat': f'Dokument PDF w stylu {style}'
            },
            'metainfo': {
                'zrodlo': 'direct_text_input',
                'tags': [style, 'direct_generation']
            }
        }
        
        if title:
            intention_data['nazwa'] = title
        
        pseudo_intention = IntentionBeing(intention_data, self.realm)
        
        return self.process_intention(pseudo_intention, {'direct_generation': True})
    
    def list_generated_documents(self) -> List[Dict[str, Any]]:
        """Zwraca listę wygenerowanych dokumentów"""
        return [
            {
                'task_id': doc['task_id'],
                'title': doc['title'],
                'style': doc['style'],
                'file_path': doc['file_path'],
                'page_count': doc['page_count'],
                'created_at': doc['created_at']
            }
            for doc in self.completed_documents
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status bytu generatora PDF"""
        base_status = super().get_status()
        
        pdf_generator_status = {
            'pdf_generator_specific': {
                'total_generated': self.total_generated,
                'successful_generations': self.successful_generations,
                'success_rate': (
                    self.successful_generations / max(1, self.total_generated)
                ),
                'average_generation_time': self.average_generation_time,
                'queue_size': len(self.generation_queue),
                'available_styles': list(self.document_styles.keys()),
                'specialized_micro_functions': len([
                    name for name in self.micro_functions.keys() 
                    if 'pdf' in name or 'generate' in name or 'parse' in name
                ]),
                'recent_documents': self.completed_documents[-5:] if self.completed_documents else []
            }
        }
        
        base_status.update(pdf_generator_status)
        return base_status
