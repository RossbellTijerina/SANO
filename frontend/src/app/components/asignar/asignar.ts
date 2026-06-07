import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { OficioService } from '../../services/oficio.service';
import { FuncionarioService } from '../../services/funcionario.service';
import { Funcionario } from '../../models/interfaces';

@Component({
  selector: 'app-asignar',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './asignar.html',
  styleUrl: './asignar.css'
})
export class AsignarComponent implements OnInit {
  anio = new Date().getFullYear();
  siguienteFolio = 0;
  expediente = '';
  solicitante = '';
  asunto = '';
  fecha = new Date().toISOString().split('T')[0];
  funcionarioId: number | null = null;
  funcionarios: Funcionario[] = [];
  loading = false;
  success = '';
  error = '';

  constructor(
    private oficioService: OficioService,
    private funcionarioService: FuncionarioService
  ) {}

  ngOnInit(): void {
    this.cargarSiguienteFolio();
    this.cargarFuncionarios();
  }

  cargarSiguienteFolio(): void {
    this.oficioService.obtenerSiguienteFolio(this.anio).subscribe({
      next: (data) => { this.siguienteFolio = data.siguiente_folio; },
      error: () => { this.siguienteFolio = 1; }
    });
  }

  cargarFuncionarios(): void {
    this.funcionarioService.listar().subscribe({
      next: (data) => { this.funcionarios = data; }
    });
  }

  onAnioChange(): void {
    this.cargarSiguienteFolio();
  }

  onSubmit(): void {
    if (!this.solicitante.trim()) {
      this.error = 'El nombre del solicitante es obligatorio';
      return;
    }
    this.loading = true;
    this.error = '';
    this.success = '';

    const data = {
      anio: this.anio,
      expediente: this.expediente,
      solicitante: this.solicitante,
      asunto: this.asunto,
      fecha: this.fecha,
      funcionario_id: this.funcionarioId
    };

    this.oficioService.crear(data).subscribe({
      next: (res) => {
        this.loading = false;
        this.success = res.mensaje;
        this.limpiarFormulario();
        this.cargarSiguienteFolio();
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.error || 'Error al crear el oficio';
      }
    });
  }

  limpiarFormulario(): void {
    this.expediente = '';
    this.solicitante = '';
    this.asunto = '';
    this.fecha = new Date().toISOString().split('T')[0];
    this.funcionarioId = null;
  }
}
