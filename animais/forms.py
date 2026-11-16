from django import forms
from django.core.exceptions import ValidationError
from .models import Solicitacao, Animal


class SolicitacaoForm(forms.ModelForm):
    termo_responsabilidade = forms.BooleanField(
        required=True,
        label="Compromisso de Tutela Responsável e Bem-Estar",
        help_text="Declaro que possuo condições financeiras, emocionais e estruturais para acolher este animal com dignidade e respeito, comprometendo-me a cumprir todas as exigências legais e sanitárias de bem-estar animal.",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Solicitacao
        fields = [
            'justificativa',
            'experiencia_animais',
            'condicoes_moradia',
        ]
        widgets = {
            'justificativa': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva sua motivação, quem mora na casa e por que você se interessou especialmente por este animal...'
            }),
            'experiencia_animais': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Você já cuidou de animais antes? Possui outros animais atualmente? Conta com médico veterinário de confiança?'
            }),
            'condicoes_moradia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descreva o local onde o animal viverá (casa, quintal com muros altos, apartamento com redes de proteção, sítio/hípica com pastagem adequada para cavalos)...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        self.animal = kwargs.pop('animal', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.animal:
            if not self.animal.is_disponivel:
                raise ValidationError(
                    f"Infelizmente o animal '{self.animal.nome}' não está mais disponível para novas solicitações (Status: {self.animal.get_status_display()})."
                )

            if self.usuario:
                solicitacao_existente = Solicitacao.objects.filter(
                    usuario=self.usuario,
                    animal=self.animal,
                    status__in=['pendente', 'em_analise']
                ).exists()

                if solicitacao_existente:
                    raise ValidationError(
                        f"Você já enviou uma solicitação em análise para '{self.animal.nome}'. Acompanhe o andamento no menu 'Minha Conta'."
                    )

        return cleaned_data

    def save(self, commit=True):
        solicitacao = super().save(commit=False)
        if self.usuario:
            solicitacao.usuario = self.usuario
        if self.animal:
            solicitacao.animal = self.animal
            # Define o tipo de solicitação com base na modalidade do animal
            solicitacao.tipo_solicitacao = 'adocao' if self.animal.modalidade == 'adocao' else 'venda'
        if commit:
            solicitacao.save()
        return solicitacao

