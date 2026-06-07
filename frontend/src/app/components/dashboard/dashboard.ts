import { Component, OnInit, ElementRef, ViewChild, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { OficioService } from '../../services/oficio.service';
import { AuthService } from '../../services/auth.service';
import { Estadisticas } from '../../models/interfaces';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class DashboardComponent implements OnInit, AfterViewInit {
  @ViewChild('chartBar') chartBarRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('chartDona') chartDonaRef!: ElementRef<HTMLCanvasElement>;

  stats: Estadisticas | null = null;
  anioSeleccionado: number = new Date().getFullYear();
  loading = true;
  chartBar: Chart | null = null;
  chartDona: Chart | null = null;
  meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

  constructor(
    private oficioService: OficioService,
    public authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.cargarEstadisticas();
  }

  ngAfterViewInit(): void {}

  cargarEstadisticas(): void {
    this.loading = true;
    this.oficioService.estadisticas(this.anioSeleccionado).subscribe({
      next: (data) => {
        this.stats = data;
        this.loading = false;
        this.cdr.detectChanges(); // Forzar actualización de UI automáticamente
        setTimeout(() => this.renderCharts(), 100);
      },
      error: () => {
        this.loading = false;
        this.cdr.detectChanges(); // Forzar actualización de UI
      }
    });
  }

  onAnioChange(): void {
    this.cargarEstadisticas();
  }

  renderCharts(): void {
    if (!this.stats) return;

    // Destroy existing charts
    this.chartBar?.destroy();
    this.chartDona?.destroy();

    // Bar Chart - Oficios por mes
    const dataPorMes = new Array(12).fill(0);
    this.stats.por_mes.forEach(m => { dataPorMes[m.mes - 1] = m.cantidad; });

    if (this.chartBarRef) {
      this.chartBar = new Chart(this.chartBarRef.nativeElement, {
        type: 'bar',
        data: {
          labels: this.meses,
          datasets: [{
            label: 'Oficios',
            data: dataPorMes,
            backgroundColor: 'rgba(105, 28, 50, 0.6)', // Guinda
            borderColor: '#691c32',
            borderWidth: 2,
            borderRadius: 6,
            borderSkipped: false,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#ffffff',
              titleColor: '#1e293b',
              bodyColor: '#475569',
              borderColor: '#e2e8f0',
              borderWidth: 1,
              cornerRadius: 8,
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: 'rgba(0,0,0,0.05)' },
              ticks: { color: '#475569' }
            },
            x: {
              grid: { display: false },
              ticks: { color: '#475569' }
            }
          }
        }
      });
    }

    // Donut Chart - Activos vs Cancelados
    if (this.chartDonaRef) {
      this.chartDona = new Chart(this.chartDonaRef.nativeElement, {
        type: 'doughnut',
        data: {
          labels: ['Activos', 'Cancelados'],
          datasets: [{
            data: [this.stats.totales.activos, this.stats.totales.cancelados],
            backgroundColor: ['rgba(46, 125, 50, 0.8)', 'rgba(198, 40, 40, 0.8)'],
            borderColor: ['#2e7d32', '#c62828'],
            borderWidth: 2,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: '#475569', padding: 16, font: { size: 12 } }
            }
          },
          cutout: '65%'
        }
      });
    }
  }
}
