import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FuncionarioService } from '../../services/funcionario.service';
import { AuthService } from '../../services/auth.service';
import { Funcionario } from '../../models/interfaces';

@Component({
  selector: 'app-funcionarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './funcionarios.html',
  styleUrl: './funcionarios.css'
})
export class FuncionariosComponent implements OnInit {
  funcionarios: Funcionario[] = [];
  loading = true;
  mensaje = '';
  mensajeTipo = '';

  // Form
  showForm = false;
  editandoId: number | null = null;
  nombre = '';
  cargo = '';
  departamento = '';

  // Delete
  eliminando: Funcionario | null = null;

  constructor(
    private funcionarioService: FuncionarioService,
    public authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.loading = true;
    this.funcionarioService.listar(false).subscribe({
      next: (data) => { this.funcionarios = data; this.loading = false; this.cdr.detectChanges(); },
      error: () => { this.loading = false; this.cdr.detectChanges(); }
    });
  }

  abrirFormulario(func?: Funcionario): void {
    this.showForm = true;
    if (func) {
      this.editandoId = func.id;
      this.nombre = func.nombre;
      this.cargo = func.cargo;
      this.departamento = func.departamento;
    } else {
      this.editandoId = null;
      this.nombre = '';
      this.cargo = '';
      this.departamento = '';
    }
  }

  cerrarFormulario(): void {
    this.showForm = false;
    this.editandoId = null;
  }

  guardar(): void {
    if (!this.nombre.trim()) {
      this.mensaje = 'El nombre es obligatorio';
      this.mensajeTipo = 'error';
      return;
    }
    const data = { nombre: this.nombre, cargo: this.cargo, departamento: this.departamento };

    const obs = this.editandoId
      ? this.funcionarioService.actualizar(this.editandoId, data)
      : this.funcionarioService.crear(data);

    obs.subscribe({
      next: () => {
        this.mensaje = this.editandoId ? 'Funcionario actualizado' : 'Funcionario creado';
        this.mensajeTipo = 'success';
        this.cerrarFormulario();
        this.cargar();
      },
      error: (err) => {
        this.mensaje = err.error?.error || 'Error al guardar';
        this.mensajeTipo = 'error';
      }
    });
  }

  confirmarEliminar(func: Funcionario): void {
    this.eliminando = func;
  }

  eliminar(): void {
    if (!this.eliminando) return;
    this.funcionarioService.eliminar(this.eliminando.id).subscribe({
      next: () => {
        this.mensaje = 'Funcionario desactivado';
        this.mensajeTipo = 'success';
        this.eliminando = null;
        this.cargar();
      },
      error: (err) => {
        this.mensaje = err.error?.error || 'Error al eliminar';
        this.mensajeTipo = 'error';
      }
    });
  }
}
