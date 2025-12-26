"use client";

import React from "react";
import { motion } from "framer-motion";
import { Package, Truck, Calendar, CreditCard, AlertCircle, FileText } from "lucide-react";

interface OrderInfo {
    order_id: string;
    customer_id: string;
    customer_name: string;
    customer_email: string;
    product_name: string;
    product_sku: string;
    quantity: number;
    price: number;
    order_date: string;
    status: string;
    shipping_address: string;
    tracking_number?: string;
    return_eligible: string;
    warranty_status: string;
    notes?: string;
}

interface OrderCardProps {
    order: OrderInfo;
    onCreateTicket: (orderId: string) => void;
}

export function OrderCard({ order, onCreateTicket }: OrderCardProps) {
    const statusColors: Record<string, string> = {
        delivered: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
        shipped: "bg-blue-500/10 text-blue-400 border-blue-500/20",
        processing: "bg-amber-500/10 text-amber-400 border-amber-500/20",
        cancelled: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    };

    const currentStatusColor = statusColors[order.status.toLowerCase()] || "bg-slate-500/10 text-slate-400 border-slate-500/20";

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl overflow-hidden shadow-2xl"
        >
            <div className="p-6 border-b border-white/5 bg-gradient-to-r from-blue-500/10 to-purple-500/10 flex justify-between items-center">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-blue-500/20 rounded-2xl">
                        <Package className="w-6 h-6 text-blue-400" />
                    </div>
                    <div>
                        <h3 className="text-white font-semibold text-lg">Order {order.order_id}</h3>
                        <p className="text-white/50 text-sm">{order.product_name}</p>
                    </div>
                </div>
                <div className={`px-4 py-1.5 rounded-full border text-xs font-bold uppercase tracking-wider ${currentStatusColor}`}>
                    {order.status}
                </div>
            </div>

            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                    <div className="flex items-start gap-3">
                        <Calendar className="w-5 h-5 text-white/30 mt-0.5" />
                        <div>
                            <p className="text-white/30 text-xs uppercase font-bold">Ordered On</p>
                            <p className="text-white/90">{new Date(order.order_date).toLocaleDateString()}</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <CreditCard className="w-5 h-5 text-white/30 mt-0.5" />
                        <div>
                            <p className="text-white/30 text-xs uppercase font-bold">Payment</p>
                            <p className="text-white/90">${order.price.toFixed(2)} ({order.quantity} item{order.quantity > 1 ? 's' : ''})</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <Truck className="w-5 h-5 text-white/30 mt-0.5" />
                        <div>
                            <p className="text-white/30 text-xs uppercase font-bold">Shipping To</p>
                            <p className="text-white/90 text-sm leading-relaxed">{order.shipping_address}</p>
                            {order.tracking_number && (
                                <p className="text-blue-400 text-xs mt-1">Tracking: {order.tracking_number}</p>
                            )}
                        </div>
                    </div>
                </div>

                <div className="space-y-4">
                    <div className="flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-white/30 mt-0.5" />
                        <div>
                            <p className="text-white/30 text-xs uppercase font-bold">Return Eligibility</p>
                            <p className={order.return_eligible === 'Yes' ? 'text-emerald-400' : 'text-rose-400'}>
                                {order.return_eligible === 'Yes' ? 'Eligible for return' : 'Final sale'}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <div className="w-full space-y-3">
                            <p className="text-white/30 text-xs uppercase font-bold">Quick Actions</p>
                            <div className="flex flex-wrap gap-2">
                                <button
                                    onClick={() => onCreateTicket(order.order_id)}
                                    className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm transition-all border border-white/5 active:scale-95"
                                >
                                    <FileText className="w-4 h-4" />
                                    Raise Ticket
                                </button>
                                {order.return_eligible === 'Yes' && (
                                    <button className="flex items-center gap-2 px-4 py-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 rounded-xl text-sm transition-all border border-emerald-500/20 active:scale-95">
                                        Initiate Return
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {order.notes && (
                <div className="px-6 pb-6 pt-2">
                    <div className="bg-black/20 rounded-2xl p-4 border border-white/5">
                        <p className="text-white/40 text-[10px] uppercase font-bold mb-1">Internal Notes</p>
                        <p className="text-white/70 text-sm italic">"{order.notes}"</p>
                    </div>
                </div>
            )}
        </motion.div>
    );
}
