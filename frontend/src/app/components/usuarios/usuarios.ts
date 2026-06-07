import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UsuarioService } from '../../services/usuario.service';
import { Usuario } from '../../models/interfaces';

@Component({
  selector: 'app-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './usuarios.html',
  styleUrl: './usuarios.css'
})
export class UsuariosComponent implements OnInit {
  usuarios: Usuario[] = [];
  loading = true;
  mensaje = '';
  mensajeTipo = '';

  showForm = false;
  editandoId: number | null = null;
  username = '';
  password = '';
  nombreCompleto = '';
  rol: 'Administrador' | 'Capturista' = 'Capturista';

  eliminando: Usuario | null = null;

  constructor(
    private usuarioService: UsuarioService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void { this.cargar(); }

  cargar(): void {
    this.loading = true;
    this.usuarioService.listar().subscribe({
      next: (data) => { this.usuarios = data; this.loading = false; this.cdr.detectChanges(); },
      error: () => { this.loading = false; this.cdr.detectChanges(); }
    });
  }

  abrirFormulario(user?: Usuario): void {
    this.showForm = true;
    if (user) {
      this.editandoId = user.id;
      this.username = user.username;
      this.password = '';
      this.nombreCompleto = user.nombre_completo;
      this.rol = user.rol;
    } else {
      this.editandoId = null;
      this.username = '';
      this.password = '';
      this.nombreCompleto = '';
      this.rol = 'Capturista';
    }
  }

  cerrarFormulario(): void { this.showForm = false; this.editandoId = null; }

  guardar(): void {
    if (!this.nombreCompleto.trim()) {
      this.mensaje = 'El nombre es obligatorio';
      this.mensajeTipo = 'error';
      return;
    }
    if (!this.editandoId && (!this.username.trim() || !this.password)) {
      this.mensaje = 'Username y contraseña son obligatorios para nuevos usuarios';
      this.mensajeTipo = 'error';
      return;
    }

    const data: any = { nombre_completo: this.nombreCompleto, rol: this.rol };
    if (!this.editandoId) {
      data.username = this.username;
      data.password = this.password;
    } else if (this.password) {
      data.password = this.password;
    }

    const obs = this.editandoId
      ? this.usuarioService.actualizar(this.editandoId, data)
      : this.usuarioService.crear(data);

    obs.subscribe({
      next: () => {
        this.mensaje = this.editandoId ? 'Usuario actualizado' : 'Usuario creado';
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

  confirmarEliminar(user: Usuario): void { this.eliminando = user; }

  eliminar(): void {
    if (!this.eliminando) return;
    this.usuarioService.eliminar(this.eliminando.id).subscribe({
      next: () => {
        this.mensaje = 'Usuario desactivado';
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
