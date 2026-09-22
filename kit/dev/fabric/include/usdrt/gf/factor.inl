// Copyright 2016 Pixar
//
// Licensed under the Apache License, Version 2.0 (the "Apache License")
// with the following modification; you may not use this file except in
// compliance with the Apache License and the following modification to it:
// Section 6. Trademarks. is deleted and replaced with:
//
// 6. Trademarks. This License does not grant permission to use the trade
//    names, trademarks, service marks, or product names of the Licensor
//    and its affiliates, except as required to comply with Section 4(c) of
//    the License and to reproduce the content of the NOTICE file.
//
// You may obtain a copy of the Apache License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the Apache License with the above modification is
// distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied. See the Apache License for the specific
// language governing permissions and limitations under the Apache License.
//
// Note: This source derived from matrix.h and matrix.cpp in USD and modified for this application.

namespace omni
{
namespace math
{
namespace linalg
{

template <typename T>
inline bool matrix4<T>::Factor(matrix4<T>* r, vec3<T>* s, matrix4<T>* u, vec3<T>* t, matrix4<T>* p, float eps) const
{
    p->SetDiagonal(1);

    matrix4<double> a;
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
            a.v[i][j] = v[i][j];
        a.v[3][i] = a.v[i][3] = 0.0;
        (*t)[i] = v[3][i];
    }
    a.v[3][3] = 1.0;

    double det = a.GetDeterminant3();
    double detSign = (det < 0.0 ? -1.0 : 1.0);
    bool isSingular = det * detSign < eps;

    matrix4<double> b = a * a.GetTranspose();
    vec3<double> eigenvalues;
    vec3<double> eigenvectors[3];
    b._Jacobi3(&eigenvalues, eigenvectors);
    matrix4<double> rTmp(eigenvectors[0][0], eigenvectors[0][1], eigenvectors[0][2], 0.0, eigenvectors[1][0],
                         eigenvectors[1][1], eigenvectors[1][2], 0.0, eigenvectors[2][0], eigenvectors[2][1],
                         eigenvectors[2][2], 0.0, 0.0, 0.0, 0.0, 1.0);

    matrix4<double> sInv;
    sInv.SetIdentity();
    for (int i = 0; i < 3; i++)
    {
        if (eigenvalues[i] < eps)
        {
            (*s)[i] = detSign * eps;
        }
        else
        {
            (*s)[i] = detSign * sqrt(eigenvalues[i]);
        }
        sInv.v[i][i] = 1.0 / (*s)[i];
    }

    *u = matrix4<T>(rTmp * sInv * rTmp.GetTranspose() * a);
    *r = matrix4<T>(rTmp);

    return !isSingular;
}

template <typename T>
inline void matrix4<T>::_Jacobi3(vec3<T>* eigenvalues, vec3<T> eigenvectors[3]) const
{
    eigenvalues->Set(v[0][0], v[1][1], v[2][2]);
    eigenvectors[0] = vec3<double>::XAxis();
    eigenvectors[1] = vec3<double>::YAxis();
    eigenvectors[2] = vec3<double>::ZAxis();

    matrix4<T> a = (*this);
    vec3<double> b = *eigenvalues;
    vec3<double> z = vec3<double>(0);

    for (int i = 0; i < 50; i++)
    {
        double sm = 0.0;
        for (int p = 0; p < 2; p++)
            for (int q = p + 1; q < 3; q++)
                sm += GfAbs(a.v[p][q]);

        if (sm == 0.0)
            return;

        double thresh = (i < 3 ? (.2 * sm / (3 * 3)) : 0.0);

        for (int p = 0; p < 3; p++)
        {
            for (int q = p + 1; q < 3; q++)
            {

                double g = 100.0 * GfAbs(a.v[p][q]);

                if (i > 3 && (GfAbs((*eigenvalues)[p]) + g == GfAbs((*eigenvalues)[p])) &&
                    (GfAbs((*eigenvalues)[q]) + g == GfAbs((*eigenvalues)[q])))
                    a.v[p][q] = 0.0;

                else if (GfAbs(a.v[p][q]) > thresh)
                {
                    double h = (*eigenvalues)[q] - (*eigenvalues)[p];
                    double t;

                    if (GfAbs(h) + g == GfAbs(h))
                    {
                        t = a.v[p][q] / h;
                    }
                    else
                    {
                        double theta = 0.5 * h / a.v[p][q];
                        t = 1.0 / (GfAbs(theta) + sqrt(1.0 + theta * theta));
                        if (theta < 0.0)
                            t = -t;
                    }

                    double c = 1.0 / sqrt(1.0 + t * t);
                    double s = t * c;
                    double tau = s / (1.0 + c);
                    h = t * a.v[p][q];
                    z[p] -= h;
                    z[q] += h;
                    (*eigenvalues)[p] -= h;
                    (*eigenvalues)[q] += h;
                    a.v[p][q] = 0.0;

                    for (int j = 0; j < p; j++)
                    {
                        g = a.v[j][p];
                        h = a.v[j][q];
                        a.v[j][p] = g - s * (h + g * tau);
                        a.v[j][q] = h + s * (g - h * tau);
                    }

                    for (int j = p + 1; j < q; j++)
                    {
                        g = a.v[p][j];
                        h = a.v[j][q];
                        a.v[p][j] = g - s * (h + g * tau);
                        a.v[j][q] = h + s * (g - h * tau);
                    }

                    for (int j = q + 1; j < 3; j++)
                    {
                        g = a.v[p][j];
                        h = a.v[q][j];
                        a.v[p][j] = g - s * (h + g * tau);
                        a.v[q][j] = h + s * (g - h * tau);
                    }

                    for (int j = 0; j < 3; j++)
                    {
                        g = eigenvectors[j][p];
                        h = eigenvectors[j][q];
                        eigenvectors[j][p] = g - s * (h + g * tau);
                        eigenvectors[j][q] = h + s * (g - h * tau);
                    }
                }
            }
        }
        for (int p = 0; p < 3; p++)
        {
            (*eigenvalues)[p] = b[p] += z[p];
            z[p] = 0;
        }
    }
}
}
}
}
