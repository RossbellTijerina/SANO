import { Routes } from '@angular/router';
import { authGuard, adminGuard } from './guards/auth.guard';

import { LoginComponent } from './components/login/login';
import { LayoutComponent } from './components/layout/layout';
import { DashboardComponent } from './components/dashboard/dashboard';
import { AsignarComponent } from './components/asignar/asignar';
import { BuscarComponent } from './components/buscar/buscar';
import { FuncionariosComponent } from './components/funcionarios/funcionarios';
import { UsuariosComponent } from './components/usuarios/usuarios';
import { ReportesComponent } from './components/reportes/reportes';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: 'dashboard', component: DashboardComponent },
      { path: 'asignar', component: AsignarComponent },
      { path: 'buscar', component: BuscarComponent },
      { path: 'reportes', component: ReportesComponent },
      { path: 'funcionarios', component: FuncionariosComponent, canActivate: [adminGuard] },
      { path: 'usuarios', component: UsuariosComponent, canActivate: [adminGuard] },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' }
    ]
  },
  { path: '**', redirectTo: 'login' }
];
