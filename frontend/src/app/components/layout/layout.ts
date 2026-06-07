import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ThemeService } from '../../services/theme.service';
import { Observable } from 'rxjs';
import { Usuario } from '../../models/interfaces';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './layout.html',
  styleUrl: './layout.css'
})
export class LayoutComponent {
  sidebarCollapsed = false;
  currentUser$: Observable<Usuario | null>;

  menuItems = [
    { icon: 'bi-speedometer2', label: 'Dashboard', route: '/dashboard' },
    { icon: 'bi-plus-circle', label: 'Asignar Oficio', route: '/asignar' },
    { icon: 'bi-search', label: 'Buscar Oficios', route: '/buscar' },
    { icon: 'bi-bar-chart-line', label: 'Reportes', route: '/reportes' },
    { icon: 'bi-people', label: 'Funcionarios', route: '/funcionarios', admin: true },
    { icon: 'bi-person-gear', label: 'Usuarios', route: '/usuarios', admin: true },
  ];

  constructor(
    public authService: AuthService, 
    private router: Router,
    public themeService: ThemeService
  ) {
    this.currentUser$ = this.authService.currentUser$;
  }

  toggleSidebar(): void {
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  isVisible(item: any): boolean {
    return !item.admin || this.authService.isAdmin();
  }
}
