import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReporteService } from '../../services/reporte.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-reportes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './reportes.html',
  styleUrl: './reportes.css'
})
export class ReportesComponent {
  anio: number = new Date().getFullYear();
  fechaDesde = '';
  fechaHasta = '';
  estado = '';
  solicitante = '';

  loadingPdf = false;
  loadingExcel = false;
  loadingBackup = false;
  mensaje = '';
  mensajeTipo = '';

  backups: any[] = [];
  showBackups = false;

  constructor(
    private reporteService: ReporteService,
    public authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  getFiltros(): any {
    const filtros: any = {};
    if (this.anio) filtros.anio = this.anio;
    if (this.fechaDesde) filtros.fecha_desde = this.fechaDesde;
    if (this.fechaHasta) filtros.fecha_hasta = this.fechaHasta;
    if (this.estado) filtros.estado = this.estado;
    if (this.solicitante) filtros.solicitante = this.solicitante;
    return filtros;
  }

  exportarPdf(): void {
    this.loadingPdf = true;
    this.reporteService.exportarPdf(this.getFiltros()).subscribe({
      next: (blob) => {
        this.descargar(blob, `reporte_oficios_${this.anio}.pdf`);
        this.loadingPdf = false;
        this.mensaje = 'Reporte PDF generado exitosamente';
        this.mensajeTipo = 'success';
        this.cdr.detectChanges();
      },
      error: () => {
        this.loadingPdf = false;
        this.mensaje = 'Error al generar el PDF';
        this.mensajeTipo = 'error';
        this.cdr.detectChanges();
      }
    });
  }

  exportarExcel(): void {
    this.loadingExcel = true;
    this.reporteService.exportarExcel(this.getFiltros()).subscribe({
      next: (blob) => {
        this.descargar(blob, `reporte_oficios_${this.anio}.xlsx`);
        this.loadingExcel = false;
        this.mensaje = 'Reporte Excel generado exitosamente';
        this.mensajeTipo = 'success';
        this.cdr.detectChanges();
      },
      error: () => {
        this.loadingExcel = false;
        this.mensaje = 'Error al generar el Excel';
        this.mensajeTipo = 'error';
        this.cdr.detectChanges();
      }
    });
  }

  crearBackup(): void {
    this.loadingBackup = true;
    this.reporteService.crearBackup().subscribe({
      next: (res) => {
        this.loadingBackup = false;
        this.mensaje = `Respaldo creado: ${res.tamano_mb} MB`;
        this.mensajeTipo = 'success';
        this.cdr.detectChanges();
        this.cargarBackups();
      },
      error: (err) => {
        this.loadingBackup = false;
        this.mensaje = err.error?.error || 'Error al crear respaldo';
        this.mensajeTipo = 'error';
        this.cdr.detectChanges();
      }
    });
  }

  cargarBackups(): void {
    this.showBackups = true;
    this.reporteService.listarBackups().subscribe({
      next: (data) => { this.backups = data; this.cdr.detectChanges(); },
      error: () => { this.cdr.detectChanges(); }
    });
  }

  private descargar(blob: Blob, nombre: string): void {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = nombre;
    a.click();
    window.URL.revokeObjectURL(url);
  }
}
