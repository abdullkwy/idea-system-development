/**
 * IDEA System - Unified React Components
 * =======================================
 * 
 * This file contains reusable React components that ensure
 * consistent UI/UX across all sections of the IDEA system.
 * 
 * Author: Manus AI
 * Date: 2025-10-20
 */

import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import '../styles/phase2_design_system.css';

/**
 * Button Component
 * Reusable button with multiple variants and sizes
 */
export const Button = ({
    children,
    variant = 'primary',
    size = 'md',
    disabled = false,
    onClick,
    className = '',
    ...props
}) => {
    const variantClass = `btn-${variant}`;
    const sizeClass = `btn-${size}`;
    const classes = `btn ${variantClass} ${sizeClass} ${className}`;

    return (
        <button
            className={classes}
            disabled={disabled}
            onClick={onClick}
            {...props}
        >
            {children}
        </button>
    );
};

Button.propTypes = {
    children: PropTypes.node.isRequired,
    variant: PropTypes.oneOf(['primary', 'secondary', 'outline', 'success', 'error']),
    size: PropTypes.oneOf(['sm', 'md', 'lg']),
    disabled: PropTypes.bool,
    onClick: PropTypes.func,
    className: PropTypes.string,
};

/**
 * Card Component
 * Container component for grouped content
 */
export const Card = ({
    children,
    header,
    footer,
    className = '',
    ...props
}) => {
    return (
        <div className={`card ${className}`} {...props}>
            {header && <div className="card-header">{header}</div>}
            <div className="card-body">{children}</div>
            {footer && <div className="card-footer">{footer}</div>}
        </div>
    );
};

Card.propTypes = {
    children: PropTypes.node.isRequired,
    header: PropTypes.node,
    footer: PropTypes.node,
    className: PropTypes.string,
};

/**
 * Input Component
 * Reusable form input with label and error handling
 */
export const Input = ({
    label,
    type = 'text',
    placeholder,
    value,
    onChange,
    error,
    disabled = false,
    required = false,
    className = '',
    ...props
}) => {
    return (
        <div className="form-group">
            {label && (
                <label>
                    {label}
                    {required && <span style={{ color: 'var(--color-error)' }}>*</span>}
                </label>
            )}
            <input
                type={type}
                placeholder={placeholder}
                value={value}
                onChange={onChange}
                disabled={disabled}
                className={className}
                {...props}
            />
            {error && <p className="text-error" style={{ marginTop: 'var(--spacing-sm)' }}>{error}</p>}
        </div>
    );
};

Input.propTypes = {
    label: PropTypes.string,
    type: PropTypes.string,
    placeholder: PropTypes.string,
    value: PropTypes.string,
    onChange: PropTypes.func,
    error: PropTypes.string,
    disabled: PropTypes.bool,
    required: PropTypes.bool,
    className: PropTypes.string,
};

/**
 * Select Component
 * Reusable dropdown select input
 */
export const Select = ({
    label,
    options,
    value,
    onChange,
    error,
    disabled = false,
    required = false,
    className = '',
    ...props
}) => {
    return (
        <div className="form-group">
            {label && (
                <label>
                    {label}
                    {required && <span style={{ color: 'var(--color-error)' }}>*</span>}
                </label>
            )}
            <select
                value={value}
                onChange={onChange}
                disabled={disabled}
                className={className}
                {...props}
            >
                <option value="">اختر خياراً</option>
                {options.map((option) => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
            {error && <p className="text-error" style={{ marginTop: 'var(--spacing-sm)' }}>{error}</p>}
        </div>
    );
};

Select.propTypes = {
    label: PropTypes.string,
    options: PropTypes.arrayOf(
        PropTypes.shape({
            value: PropTypes.string.isRequired,
            label: PropTypes.string.isRequired,
        })
    ).isRequired,
    value: PropTypes.string,
    onChange: PropTypes.func,
    error: PropTypes.string,
    disabled: PropTypes.bool,
    required: PropTypes.bool,
    className: PropTypes.string,
};

/**
 * Textarea Component
 * Reusable textarea input
 */
export const Textarea = ({
    label,
    placeholder,
    value,
    onChange,
    error,
    rows = 4,
    disabled = false,
    required = false,
    className = '',
    ...props
}) => {
    return (
        <div className="form-group">
            {label && (
                <label>
                    {label}
                    {required && <span style={{ color: 'var(--color-error)' }}>*</span>}
                </label>
            )}
            <textarea
                placeholder={placeholder}
                value={value}
                onChange={onChange}
                rows={rows}
                disabled={disabled}
                className={className}
                {...props}
            />
            {error && <p className="text-error" style={{ marginTop: 'var(--spacing-sm)' }}>{error}</p>}
        </div>
    );
};

Textarea.propTypes = {
    label: PropTypes.string,
    placeholder: PropTypes.string,
    value: PropTypes.string,
    onChange: PropTypes.func,
    error: PropTypes.string,
    rows: PropTypes.number,
    disabled: PropTypes.bool,
    required: PropTypes.bool,
    className: PropTypes.string,
};

/**
 * Alert Component
 * Display alert messages with different severity levels
 */
export const Alert = ({
    type = 'info',
    message,
    onClose,
    dismissible = true,
}) => {
    const [visible, setVisible] = useState(true);

    const handleClose = useCallback(() => {
        setVisible(false);
        if (onClose) onClose();
    }, [onClose]);

    if (!visible) return null;

    const typeClass = `text-${type}`;
    const bgColor = {
        success: 'rgba(39, 174, 96, 0.1)',
        error: 'rgba(231, 76, 60, 0.1)',
        warning: 'rgba(243, 156, 18, 0.1)',
        info: 'rgba(52, 152, 219, 0.1)',
    }[type];

    return (
        <div
            style={{
                backgroundColor: bgColor,
                padding: 'var(--spacing-md)',
                borderRadius: 'var(--border-radius-md)',
                marginBottom: 'var(--spacing-md)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
            }}
        >
            <p className={typeClass}>{message}</p>
            {dismissible && (
                <button
                    onClick={handleClose}
                    style={{
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        fontSize: '1.5rem',
                    }}
                >
                    ×
                </button>
            )}
        </div>
    );
};

Alert.propTypes = {
    type: PropTypes.oneOf(['success', 'error', 'warning', 'info']),
    message: PropTypes.string.isRequired,
    onClose: PropTypes.func,
    dismissible: PropTypes.bool,
};

/**
 * Modal Component
 * Reusable modal dialog
 */
export const Modal = ({
    isOpen,
    onClose,
    title,
    children,
    footer,
    size = 'md',
}) => {
    if (!isOpen) return null;

    const sizeStyles = {
        sm: { maxWidth: '400px' },
        md: { maxWidth: '600px' },
        lg: { maxWidth: '800px' },
    };

    return (
        <div
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
            }}
            onClick={onClose}
        >
            <div
                style={{
                    backgroundColor: 'var(--color-bg-primary)',
                    borderRadius: 'var(--border-radius-lg)',
                    boxShadow: 'var(--shadow-2xl)',
                    ...sizeStyles[size],
                    maxHeight: '90vh',
                    overflow: 'auto',
                }}
                onClick={(e) => e.stopPropagation()}
            >
                <div
                    style={{
                        padding: 'var(--spacing-lg)',
                        borderBottom: '1px solid var(--color-border)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                    }}
                >
                    <h2>{title}</h2>
                    <button
                        onClick={onClose}
                        style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            fontSize: '1.5rem',
                        }}
                    >
                        ×
                    </button>
                </div>
                <div style={{ padding: 'var(--spacing-lg)' }}>
                    {children}
                </div>
                {footer && (
                    <div
                        style={{
                            padding: 'var(--spacing-lg)',
                            borderTop: '1px solid var(--color-border)',
                            display: 'flex',
                            justifyContent: 'flex-end',
                            gap: 'var(--spacing-md)',
                        }}
                    >
                        {footer}
                    </div>
                )}
            </div>
        </div>
    );
};

Modal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    title: PropTypes.string.isRequired,
    children: PropTypes.node.isRequired,
    footer: PropTypes.node,
    size: PropTypes.oneOf(['sm', 'md', 'lg']),
};

/**
 * Navigation Component
 * Reusable navigation bar
 */
export const Navigation = ({
    items,
    activeItem,
    onItemClick,
    logo,
}) => {
    return (
        <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {logo && <div style={{ fontWeight: 'bold', fontSize: '1.5rem' }}>{logo}</div>}
            <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
                {items.map((item) => (
                    <a
                        key={item.id}
                        href={item.href}
                        className={activeItem === item.id ? 'active' : ''}
                        onClick={(e) => {
                            e.preventDefault();
                            onItemClick(item.id);
                        }}
                    >
                        {item.label}
                    </a>
                ))}
            </div>
        </nav>
    );
};

Navigation.propTypes = {
    items: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.string.isRequired,
            label: PropTypes.string.isRequired,
            href: PropTypes.string,
        })
    ).isRequired,
    activeItem: PropTypes.string,
    onItemClick: PropTypes.func,
    logo: PropTypes.string,
};

/**
 * Loading Spinner Component
 * Display loading state
 */
export const LoadingSpinner = ({ size = 'md' }) => {
    const sizeStyles = {
        sm: { width: '20px', height: '20px' },
        md: { width: '40px', height: '40px' },
        lg: { width: '60px', height: '60px' },
    };

    return (
        <div
            style={{
                ...sizeStyles[size],
                border: '4px solid var(--color-border)',
                borderTop: '4px solid var(--color-primary-olive)',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
            }}
        />
    );
};

LoadingSpinner.propTypes = {
    size: PropTypes.oneOf(['sm', 'md', 'lg']),
};

/**
 * Pagination Component
 * Display pagination controls
 */
export const Pagination = ({
    currentPage,
    totalPages,
    onPageChange,
}) => {
    const pages = [];
    const maxVisible = 5;

    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);

    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
    }

    return (
        <div style={{ display: 'flex', gap: 'var(--spacing-sm)', justifyContent: 'center' }}>
            <Button
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 1}
                variant="secondary"
                size="sm"
            >
                السابق
            </Button>

            {startPage > 1 && (
                <>
                    <Button
                        onClick={() => onPageChange(1)}
                        variant={currentPage === 1 ? 'primary' : 'secondary'}
                        size="sm"
                    >
                        1
                    </Button>
                    {startPage > 2 && <span>...</span>}
                </>
            )}

            {pages.map((page) => (
                <Button
                    key={page}
                    onClick={() => onPageChange(page)}
                    variant={currentPage === page ? 'primary' : 'secondary'}
                    size="sm"
                >
                    {page}
                </Button>
            ))}

            {endPage < totalPages && (
                <>
                    {endPage < totalPages - 1 && <span>...</span>}
                    <Button
                        onClick={() => onPageChange(totalPages)}
                        variant={currentPage === totalPages ? 'primary' : 'secondary'}
                        size="sm"
                    >
                        {totalPages}
                    </Button>
                </>
            )}

            <Button
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                variant="secondary"
                size="sm"
            >
                التالي
            </Button>
        </div>
    );
};

Pagination.propTypes = {
    currentPage: PropTypes.number.isRequired,
    totalPages: PropTypes.number.isRequired,
    onPageChange: PropTypes.func.isRequired,
};

export default {
    Button,
    Card,
    Input,
    Select,
    Textarea,
    Alert,
    Modal,
    Navigation,
    LoadingSpinner,
    Pagination,
};

