import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { OficioService } from '../../services/oficio.service';
import { FuncionarioService } from '../../services/funcionario.service';
import { AuthService } from '../../services/auth.service';
import { Oficio, Funcionario } from '../../models/interfaces';

@Component({
  selector: 'app-buscar',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './buscar.html',
  styleUrl: './buscar.css'
})
export class BuscarComponent implements OnInit {
  // Filtros
  filtroAnio: string = '';
  filtroFolio: string = '';
  filtroExpediente: string = '';
  filtroSolicitante: string = '';
  filtroAsunto: string = '';
  filtroFechaDesde: string = '';
  filtroFechaHasta: string = '';
  filtroFuncionarioId: string = '';
  filtroEstado: string = '';

  funcionarios: Funcionario[] = [];
  resultados: Oficio[] = [];
  loading = false;
  searched = false;

  // Edición
  editando: Oficio | null = null;
  editExpediente = '';
  editSolicitante = '';
  editAsunto = '';
  editFuncionarioId: number | null = null;

  // Cancelación
  cancelando: Oficio | null = null;
  motivoCancelacion = '';

  mensaje = '';
  mensajeTipo = '';

  constructor(
    private oficioService: OficioService,
    private funcionarioService: FuncionarioService,
    public authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.funcionarioService.listar().subscribe({
      next: (data) => { this.funcionarios = data; }
    });
  }

  buscar(): void {
    this.loading = true;
    this.searched = true;
    this.mensaje = '';
    const filtros: any = {};
    if (this.filtroAnio) filtros.anio = this.filtroAnio;
    if (this.filtroFolio) filtros.folio = this.filtroFolio;
    if (this.filtroExpediente) filtros.expediente = this.filtroExpediente;
    if (this.filtroSolicitante) filtros.solicitante = this.filtroSolicitante;
    if (this.filtroAsunto) filtros.asunto = this.filtroAsunto;
    if (this.filtroFechaDesde) filtros.fecha_desde = this.filtroFechaDesde;
    if (this.filtroFechaHasta) filtros.fecha_hasta = this.filtroFechaHasta;
    if (this.filtroFuncionarioId) filtros.funcionario_id = this.filtroFuncionarioId;
    if (this.filtroEstado) filtros.estado = this.filtroEstado;

    this.oficioService.buscar(filtros).subscribe({
      next: (data) => {
        this.resultados = data.oficios;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => { this.loading = false; this.cdr.detectChanges(); }
    });
  }

  limpiarFiltros(): void {
    this.filtroAnio = '';
    this.filtroFolio = '';
    this.filtroExpediente = '';
    this.filtroSolicitante = '';
    this.filtroAsunto = '';
    this.filtroFechaDesde = '';
    this.filtroFechaHasta = '';
    this.filtroFuncionarioId = '';
    this.filtroEstado = '';
    this.resultados = [];
    this.searched = false;
  }

  // ---- Edición ----
  abrirEdicion(o: Oficio): void {
    this.editando = o;
    this.editExpediente = o.expediente;
    this.editSolicitante = o.solicitante;
    this.editAsunto = o.asunto;
    this.editFuncionarioId = o.funcionario_id;
    this.cancelando = null;
  }

  guardarEdicion(): void {
    if (!this.editando) return;
    const data = {
      expediente: this.editExpediente,
      solicitante: this.editSolicitante,
      asunto: this.editAsunto,
      funcionario_id: this.editFuncionarioId
    };
    this.oficioService.actualizar(this.editando.id, data).subscribe({
      next: () => {
        this.mensaje = 'Oficio actualizado correctamente';
        this.mensajeTipo = 'success';
        this.editando = null;
        this.buscar();
      },
      error: (err) => {
        this.mensaje = err.error?.error || 'Error al actualizar';
        this.mensajeTipo = 'error';
      }
    });
  }

  cerrarEdicion(): void { this.editando = null; }

  // ---- Cancelación ----
  abrirCancelacion(o: Oficio): void {
    this.cancelando = o;
    this.motivoCancelacion = '';
    this.editando = null;
  }

  confirmarCancelacion(): void {
    if (!this.cancelando || !this.motivoCancelacion.trim()) return;
    this.oficioService.cancelar(this.cancelando.id, this.motivoCancelacion).subscribe({
      next: () => {
        this.mensaje = 'Oficio cancelado correctamente';
        this.mensajeTipo = 'success';
        this.cancelando = null;
        this.buscar();
      },
      error: (err) => {
        this.mensaje = err.error?.error || 'Error al cancelar';
        this.mensajeTipo = 'error';
      }
    });
  }

  cerrarCancelacion(): void { this.cancelando = null; }
}
