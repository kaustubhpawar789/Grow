# Project Context: Mutual Fund FAQ Assistant

## Background
The mutual fund landscape is filled with complex information. Retail investors and customer support teams often struggle to quickly find simple, factual details about specific mutual fund schemes, such as expense ratios, exit loads, fund management data, or minimum SIP amounts. The goal of this project is to create a reliable and factual FAQ assistant to streamline this process. 

## Project Objective
To build a lightweight **Retrieval-Augmented Generation (RAG)-based** FAQ assistant specifically for mutual fund schemes (using Groww as the product context reference). 

The assistant is strictly constrained to provide **facts-only** answers. It must retrieve and present objective information from official sources while rigorously avoiding any form of financial or investment advice.

## Target Audience
1. **Retail Investors**: Users who want to quickly check facts (like lock-in periods, benchmark indices, or AUM) while comparing mutual fund schemes.
2. **Customer Support & Content Teams**: Internal teams who need a fast, reliable tool to handle repetitive client queries about mutual funds.

## Key Principles & Guardrails
- **Facts-Only**: The assistant must never provide opinions, return predictions, performance comparisons, or investment recommendations.
- **Official Sources Only**: All answers must be grounded strictly in data from authorized public sources (e.g., Asset Management Companies (AMCs), AMFI, and SEBI). No third-party blogs or aggregators.
- **Privacy First**: The system must not collect, process, or store Personally Identifiable Information (PII) such as PAN, Aadhaar, OTPs, email addresses, or Account Numbers.
- **Verifiable Transparency**: Every generated response must be short (max 3 sentences) and include exactly one source citation link and a "last updated" timestamp to ensure complete transparency and verifiability.

## Summary
By prioritizing accuracy over speculative intelligence, this project aims to deliver a trustworthy, transparent, and compliant mutual fund assistant. It will provide a simple, minimalistic UI allowing users to ask factual queries and receive verified, source-backed financial information safely.
