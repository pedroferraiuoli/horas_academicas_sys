from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image
)
from reportlab.lib.enums import TA_CENTER
from django.conf import settings
from datetime import datetime
import os


class RelatorioAlunoPdfBuilder:

    def __init__(self, *, response, dados):
        self.response = response
        self.dados = dados
        self.aluno = dados['aluno']
        self.elements = []
        self._setup_styles()

    def build(self):
        doc = SimpleDocTemplate(
            self.response,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        self._add_logo()
        self._add_header()
        self._add_info_aluno()
        self._add_categorias()
        self._add_resumo()
        self._add_footer()

        doc.build(self.elements)

    # =====================
    # ESTILOS
    # =====================
    def _setup_styles(self):
        styles = getSampleStyleSheet()

        self.style_title = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a4d8f'),
            alignment=TA_CENTER,
            spaceAfter=30
        )

        self.style_heading = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a4d8f'),
            spaceAfter=12,
            spaceBefore=12
        )

        self.style_normal = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )

    # =====================
    # BLOCOS
    # =====================
    def _add_logo(self):
        logo_path = os.path.join(
            settings.BASE_DIR,
            'atividades', 'static', 'images', 'logoiff.png'
        )
        if os.path.exists(logo_path):
            img = Image(logo_path, width=4*cm, height=4*cm)
            img.hAlign = 'CENTER'
            self.elements.append(img)
            self.elements.append(Spacer(1, 0.5*cm))

    def _add_header(self):
        self.elements.append(
            Paragraph("RELATÓRIO DE ATIVIDADES COMPLEMENTARES", self.style_title)
        )

    def _add_info_aluno(self):
        aluno = self.aluno

        data = [
            ['Aluno:', aluno.nome],
            ['Matrícula:', aluno.matricula],
            ['Curso:', aluno.curso.nome],
            ['Data:', datetime.now().strftime('%d/%m/%Y')],
        ]

        table = Table(data, colWidths=[4*cm, 13*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        self.elements.append(table)
        self.elements.append(Spacer(1, 0.8*cm))

    def _add_categorias(self):
        for item in self.dados['categorias']:
            categoria = item['categoria']
            atividades = item['atividades']

            titulo = f"{categoria.categoria.nome} (Limite: {categoria.limite_horas}h)"
            self.elements.append(Paragraph(titulo, self.style_heading))

            table_data = [['Atividade', 'Horas Aprovadas']]

            for ativ in atividades:
                table_data.append([
                    ativ.nome[:50],
                    f"{ativ.horas_aprovadas if ativ.horas_aprovadas is not None else 0}h"
                ])

            subtotal = (
                f"<b>Subtotal: {item['horas_brutas']}h</b>"
                f"<br/>Válidas: {item['horas_validas']}h"
            )

            table_data.append([Paragraph(subtotal, self.style_normal), ''])

            table = Table(table_data, colWidths=[10*cm, 3.5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a4d8f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
                ('SPAN', (0, -1), (1, -1)),
            ]))

            self.elements.append(table)
            self.elements.append(Spacer(1, 0.6*cm))

    def _add_resumo(self):
        total = self.dados['total_horas_validas']
        req = self.dados['horas_requeridas']
        faltam = max(0, req - total)
        perc = (total / req * 100) if req else 0

        self.elements.append(Paragraph("RESUMO GERAL", self.style_heading))

        data = [
            ['Horas válidas:', f'{total}h'],
            ['Horas requeridas:', f'{req}h'],
            ['Horas faltantes:', f'{faltam}h'],
            ['Percentual:', f'{perc:.1f}%'],
        ]

        table = Table(data, colWidths=[11*cm, 6*cm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1a4d8f')),
        ]))

        self.elements.append(table)

    def _add_footer(self):
        self.elements.append(Spacer(1, 1.5*cm))
        self.elements.append(
            Paragraph(
                f'Gerado em {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                self.style_normal
            )
        )
