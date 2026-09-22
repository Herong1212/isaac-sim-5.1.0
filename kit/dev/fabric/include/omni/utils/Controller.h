// Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once


namespace omni
{

// Simple proportional, derivative, integral controller
struct PIDController
{
    static constexpr float kIntegralLimit = 5.0f;

    PIDController(float kp, float ki, float kd, float kdSmooth, float kdDecay)
        : m_kp(kp)
        , m_ki(ki)
        , m_kd(kd)
        , m_kdSmooth(kdSmooth)
        , m_kdDecay(kdDecay)
        , m_prev_actual(0)
        , m_derivativeSmooth(0)
        , m_integral(0)
    {}

    float update(float setpoint, float actual, float deadZoneMin, float deadZoneMax)
    {
        float error = setpoint - actual;

        if ((error >= deadZoneMin) && (error <= deadZoneMax))
        {
            m_integral = 0;
            m_prev_actual = actual;
            return 0;
        }

        // Proportional term
        float p = m_kp * error;

        // Integral term
        m_integral += error;
        m_integral = std::min(m_integral, setpoint * kIntegralLimit);
        m_integral = std::max(m_integral, -setpoint * kIntegralLimit);
        float i = m_ki * m_integral;

        // Derivative term
        float derivative = m_prev_actual - actual;
        float d = m_kd * derivative;

        m_derivativeSmooth = m_derivativeSmooth * m_kdDecay + derivative * (1.0f - m_kdDecay);
        float dS = m_kdSmooth * m_derivativeSmooth;

        // Calculate the control output
        float control_output = p + i + d + dS;

        // Update previous error for the next iteration
        m_prev_actual = actual;

        return control_output;
    }

    void reachedLimits()
    {
        m_integral = 0;
        m_derivativeSmooth = 0;
    }

    float m_kp;           // Proportional constant
    float m_ki;           // Integral constant
    float m_kd;           // Derivative constant
    float m_kdSmooth;     // Derivative smoothed constant
    float m_kdDecay;     // Derivative smoothing decay
    float m_prev_actual;   // Previous error
    float m_derivativeSmooth;   // Previous error
    float m_integral;     // Integral term accumulator
};

} // namespace omni
