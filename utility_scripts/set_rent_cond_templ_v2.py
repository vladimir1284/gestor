from template_admin.models.template_version import TemplateVersion

TemplRentV2 = """
<div class="raw-html-embed">
    <h1 style="text-align:center; background-color: rgba(105, 108, 255, 0.16); border-top: 2px solid gray; border-bottom: 2px solid gray;">
                EQUIPMENT LEASE
    </h1>
</div>
<ol>
    <li>
        <p style="text-align:justify;">
            <u>Parties</u> This <i>Equipment Lease</i> (“Lease”) is made by the following Parties:
        </p>
        <figure class="table" style="width:100%;">
            <table>
                <tbody>
                    <tr>
                        <td style="vertical-align:top;">
                            A.
                        </td>
                        <td style="vertical-align:top;">
                            <strong><u>Lessor:</u></strong>
                        </td>
                        <td style="vertical-align:top;">
                            TOWITHOUSTON LLC, a Texas limited liability company, TXSOS File 804200199
                        </td>
                    </tr>
                    <tr>
                        <td style="vertical-align:top;">
                            &nbsp;
                        </td>
                        <td style="vertical-align:top;">
                            <u>Address:</u>
                        </td>
                        <td style="vertical-align:top;">
                            6514 Mohave Ln., Richmond, Texas 77469
                        </td>
                    </tr>
                    <tr>
                        <td style="vertical-align:top;">
                            &nbsp;
                        </td>
                        <td style="vertical-align:top;">
                            <u>E-Mail</u>:
                        </td>
                        <td style="vertical-align:top;">
                            <a href="mailto:towithouson@gmail.com"><span style="color:#0000ff;"><u>towithouson@gmail.com</u></span></a>&nbsp;
                        </td>
                    </tr>
                    <tr>
                        <td style="vertical-align:top;">
                            &nbsp;
                        </td>
                        <td style="vertical-align:top;">
                            <u>Telephone</u>:
                        </td>
                        <td style="vertical-align:top;">
                            (832) 963-5145 / (305) 833-6104
                        </td>
                    </tr>
                    <tr>
                        <td style="vertical-align:top;">
                            B.
                        </td>
                        <td style="vertical-align:top;">
                            <strong><u>Lessee:</u></strong>
                        </td>
                        <td style="vertical-align:top;">
                            <mark class="marker-yellow"><u>{{ contract.lessee.name }}</u></mark>
                        </td>
                    </tr>
                    <tr>
                        <td style="vertical-align:top;">
                            &nbsp;
                        </td>
                        <td style="vertical-align:top;">
                            Physical Address:
                        </td>
                        <td style="vertical-align:top;">
                            <mark class="marker-yellow"><u>{{ contract.lessee.data.client_address }}</u></mark>
                        </td>
                    </tr>
                    <tr>
                        <td style="vertical-align:top;">
                            &nbsp;
                        </td>
                        <td style="vertical-align:top;">
                            E-Mail:
                        </td>
                        <td style="vertical-align:top;">
                            <mark class="marker-yellow"><u>{{ contract.lessee.email }}</u></mark>
                        </td>
                    </tr>
                    <tr>
                        <td style="vertical-align:top;">
                            &nbsp;
                        </td>
                        <td style="vertical-align:top;">
                            Telephone:
                        </td>
                        <td style="vertical-align:top;">
                            <mark class="marker-yellow"><u>{{ contract.lessee.phone_number }}</u></mark>
                        </td>
                    </tr>
                </tbody>
            </table>
        </figure>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Effective Date</u> This Lease is effective <mark class="marker-yellow"><u>{{ contract.effective_date|date:'F d, Y' }}</u></mark>.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Equipment Leased</u>&nbsp;Lessor leases to Lessee and Lessee leases from Lessor, according to the provisions of this Lease, the Equipment described on the <u>Exhibit A</u> <i>Equipment Schedule</i> attached as part of this Lease.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Term</u>&nbsp;The Term of this Lease shall be <mark class="marker-yellow"><u>{{ contract.contract_term }}</u></mark> months, from <mark class="marker-yellow"><u>{{ contract.effective_date|date:'F d, Y' }}</u></mark> (“Commencement Date”), to <mark class="marker-yellow"><u>{{ contract.end_date|date:'F d, Y' }}</u></mark>, unless the Term is ended sooner or later by operation of other provisions of this Lease (said ending date, whenever it may occur, being the “Termination Date”). Lessee may extend the Term automatically month-to-month by continuing to fully and timely perform all the Lessee’s obligations until Lessor gives notice to end the Lease. The “Term” of this Lease shall run from Commencement Date to Termination Date.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Rent</u>&nbsp;Lessee shall pay to Lessor $ <mark class="marker-yellow"><u>{{ contract.payment_amount }}</u></mark> as monthly rent throughout the Term of this Lease. Monthly rent shall be paid in advance, on the first day of each calendar month for which due, without deduction, offset, abatement, notice, or demand, and continuing on the first day of each and every month thereafter throughout the Term.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Prorated rent</u>&nbsp;Rent payments for a period less than a full calendar month shall be paid on the first day of such period and prorated by the number of days in the period divided over the number of days in that month.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Late Charge</u>&nbsp;Lessee shall pay a late charge of $&nbsp;200.00 on any monthly rent payment received by Lessor after the 7th day of the month when due, to cover Lessor’s additional administrative expense for processing late receipts. Lessor shall be entitled to late charges in addition to, and not in lieu of, all other remedies available to Lessor.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Security Deposit</u> Lessee shall pay to Lessor $&nbsp;<mark class="marker-yellow"><u>{{ contract.security_deposit }}</u></mark> as security deposit at the time of signing of this Lease. Thereafter, if Lessee defaults in any obligation under this Lease, Lessor may (but is not required to) apply a portion or all of the security deposit toward the discharge of such obligation in default, and Lessee shall reimburse to Lessor the sum so applied within ten (10) days after delivery of Lessor’s written demand. Lessor may commingle the security deposit with other funds of the Lessor, and any interest earned shall be the property of Lessor. Provided that Lessee has not defaulted in any obligation under this Lease, Lessor shall refund the security deposit to Lessee, without interest, in accordance with the Texas Property Code.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Use</u>&nbsp;Lessee shall use the Equipment for freight road transportation only. No other use is allowed without the Lessor’s prior written consent.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Location of Equipment</u>&nbsp;Lessee shall keep the Equipment at Lessee’s physical address listed above at all times, except only when transporting freight or undergoing maintenance or repairs.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Compliance with Laws</u>&nbsp;Lessee shall use the Equipment in compliance with all laws, ordinances, orders, rules, and regulations of federal, state, municipal, or other agencies or bodies having jurisdiction over Lessee’s use of the Equipment, including (but not limited to) licensing and registration requirements, motor vehicle laws, and load weight and safety standards by the Texas Department of Transportation, Texas Department of Motor Vehicles, and U.S. Department of Transportation. Lessee shall not engage in or tolerate any criminal or unlawful activity involving the Equipment. Lessee shall immediately provide Lessor with notice (and a copy if applicable) of any communication to Lessee from a federal, state, municipal, or local authority concerning criminal or unlawful activity.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Acceptance of Equipment</u>&nbsp;Lessee shall inspect promptly all items of Equipment delivered to Lessee pursuant to this Lease. Lessee shall immediately notify Lessor in writing of any discrepancies between any item received and its description on <u>Exhibit A</u>. If such written notice does not issue within three (3) calendar days after delivery of the item, it shall be conclusively presumed the item was accepted by Lessee in its condition as listed on <u>Exhibit A</u>.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Maintenance and Repairs</u>&nbsp;Lessee shall, at Lessee’s sole expense, maintain the Equipment in a good state of repair. Lessee shall make and pay for all repairs and replacements to the Equipment which may become necessary from damage or from wear and tear or the effect of time or the natural elements, or which may become required by applicable laws, codes, rules or regulations. Lessee shall continuously monitor and inspect the Equipment to insure all maintenance, repair, and replacement needs are being promptly met on an ongoing basis. Lessor also may (but is not obligated to) notify Lessee about any condition requiring maintenance, repair, or replacement by Lessee.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>No Alterations to Equipment</u>&nbsp;Lessee shall not alter or modify the Equipment without first obtaining Lessor’s written approval of Lessee’s plans and specifications, selection of materials, and choice of contractors for the intended work.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Lessor’s Right of Inspection</u>&nbsp;Lessor shall have the right (but not the obligation) to inspect the Equipment at Lessee’s location from time to time, during regular business hours, without interference or hindrance from Lessee. Lessee expressly waives any claim for damages for interference with, inconvenience, or injury to Lessee’s business and for loss of enjoyment or use of the Equipment arising from Lessor’s right of inspection.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Payment of Tolls</u>&nbsp;Lessee shall pay all tolls-by-plate charges incurred from use of the Equipment within seven (7) days after being notified by Lessor of such charges.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Surrender of Equipment</u>&nbsp;At the end of the Term, Lessee shall deliver and surrender the Equipment to Lessor at any address Lessor shall designate within Harris or Fort Bend County, Texas, in good condition (ordinary wear and tear excepted) but with new tires and wiring.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Disclaimer of Warranties</u>&nbsp;LESSEE EXPRESSLY ACKNOWLEDGES THAT LESSOR HAS NOT MADE AND DOES NOT MAKE ANY REPRESENTATIONS OR WARRANTIES ABOUT THE CONDITION OF THE EQUIPMENT, AND THAT LESSOR DISCLAIMS ANY AND ALL REPRESENTATIONS, WARRANTIES, AND GUARANTEES OF ANY KIND OR NATURE, ORAL OR WRITTEN, EXPRESS, IMPLIED, OR ARISING BY OPERATION OF LAW, CONCERNING THE EQUIPMENT, INCLUDING WITHOUT LIMITATION IMPLIED WARRANTIES OF SUITABILITY, DESIGN, CONDITION, AND FITNESS FOR A PARTICULAR USE OR PURPOSE.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Certification of Credit Information</u>&nbsp;Lessee certifies that all information and documents provided by Lessee to Lessor prior to signing this Lease (including, but not limited to, lease application, trade and credit references, financial reports, letters of reference, personal and work history, bank records, etc.) is true and correct. In the event any such information or document should be found to be untrue or incorrect, Lessor may then declare Lessee to be in default, terminate this Lease, and enforce all remedies provided in this Lease against default.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Liability Insurance</u>&nbsp;Lessee shall obtain and keep in force during the term of this Lease liability insurance protecting Lessor and Lessee against liability in connection with the use of the Equipment, for an amount of not less than One Million Dollars ($&nbsp;1,000,000) for personal injury or death and One Hundred Thousand Dollars ($&nbsp;100,000) for property damage. The policy shall name Lessor as additional insured. The liability insurer shall be a reputable company acceptable to Lessor. The policy must provide that coverage shall be not cancelable or subject to reduction or modification without at least thirty (30) days’ prior written notice to Lessor from the insurer.&nbsp;
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Casualty Insurance</u>&nbsp;Lessee shall obtain and keep in force during the Term of this Lease a policy of casualty insurance covering loss or damage to the Equipment against fire, explosion, vandalism, theft, malicious mischief, collision, or accident. The policy shall provide coverage for loss up to the replacement value of the Equipment, with a deductible amount not greater than $&nbsp;5,000 per occurrence, with Lessor listed as loss co-payee and additional insured.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Proof of Insurance Compliance</u>&nbsp;Within three (3) days after Lessor’s request, Lessee shall deliver to Lessor the liability and casualty insurance policies or a certificate of liability and casualty insurance evidencing compliance with this Lease.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Risk of Loss or Damage</u>&nbsp;Lessee assumes and accepts absolutely all risk for loss or damage to the Equipment and upon demand shall compensate Lessor for any loss or damage regardless of cause (such as from Lessee’s negligence, from a third party’s negligence, without anybody’s negligence, or while being operated with or without Lessee’s permission or knowledge).
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Indemnity and Hold Harmless</u>&nbsp;Lessor shall not be liable to Lessee or to any other person, and Lessee shall indemnify and hold Lessor harmless, from any and all claims arising in whole or in part from Lessee’s use of the Equipment, or from breach or default by Lessee under this Lease, or from any negligence of Lessee or Lessee’s employees, contractors, or agents. <strong>Further, Lessee expressly assumes all risk of damage to property or injury to persons related in any way to lessee’s use of the equipment. LESSEE AGREES TO INDEMNIFY, DEFEND, AND HOLD LESSOR HARMLESS FROM LOSS, ATTORNEY’S FEES, EXPENSES, CLAIMS, OR JUDGMENTS ARISING OUT OF ANY SUCH DAMAGE, OR INJURY. </strong>Moreover, if an action is brought against Lessor on any such claim, Lessee shall defend the same at Lessee’s expense by legal counsel satisfactory to Lessor. This indemnity, hold-harmless covenant, and liability exemption in favor of Lessor shall continue in full force and effect after the end of this Lease.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Assignment by Lessor</u>&nbsp;Lessor may sell or assign the Lessor’s rights and obligations under this Lease. Any such transfer shall release Lessor from further liability under this Lease.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>No Assignment by Lessee</u>&nbsp;Lessee shall not assign this Lease or sublease the Equipment without Lessor’s prior written consent. Any attempt to assign Lessee’s interest in this Lease or to sublet the Equipment shall be deemed a material default of this Lease.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Ownership of Equipment</u>&nbsp;The Equipment constitutes personal property owned by Lessor, regardless of whether attached to any freight truck or machinery. Lessee shall immediately notify Lessor about any claim, lien, levy, or legal process involving the Equipment.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Repossession</u>&nbsp;Lessee hereby expressly grants to Lessor a contractual security interest on the Equipment so that upon any default by Lessee under this Lease, Lessor or Lessor’s agents may peaceably enter any premises where the Equipment is located and secure, remove, or otherwise take possession of Equipment.<span style="color:#000000;"> </span>If Lessor repossesses Equipment with a third-party’s property contained in, carried on, or attached to the Equipment, then: (a)&nbsp;Lessor may take possession of such property and hold it in Lessor's possession or in public storage; (b)&nbsp;any costs, fees, or expenses associated with such possession or public storage shall be borne fully by Lessee; and (c)&nbsp;Lessee shall remain solely liable for, and shall indemnify and hold Lessor harmless from, any damage to such property.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Defaul</u>t&nbsp;The occurrence of any one or more of the following events shall constitute a material default of this Lease: (a)&nbsp;Lessee violates any law, ordinance, order, rule, or regulation of a federal, state, municipal, or other governmental agency or body concerning the use of the Equipment; (b)&nbsp;Lessee abandons or attempts to abandon the Equipment; (c)&nbsp;Lessee transfers, assigns, or attempts to transfer or assign Lessee’s interest in this Lease or the Equipment; (d)&nbsp;Lessee fails to make when due any payment of rent or other payment required by this Lease; (e)&nbsp;Lessee breaches any other obligation under this Lease where such breach continues for ten (10) days after written notice from Lessor; (f)&nbsp;Lessee becomes insolvent or unable to pay debts when due; (g)&nbsp;Lessee becomes the debtor in a voluntary or involuntary bankruptcy; or (h)&nbsp;any information or document provided by Lessee to Lessor prior to signing this Lease is found to be untrue or incorrect.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Remedies</u>&nbsp;In the event of a default by Lessee, Lessor may at any time thereafter, with or without notice or demand and without limiting the exercise of any other legal right or remedy available to Lessor, terminate this Lease, and Lessee shall immediately surrender possession of the Equipment to Lessor. Additionally, upon Lessee’s default Lessor shall be entitled to recover from Lessee all the resulting damages, including, but not limited to: the cost of recovering possession of the Equipment, the cost of repairing the Equipment to a good functioning condition, delinquent rent, reasonable attorney’s fees, court costs, and the then present value of the rent remaining unpaid or that would be payable in the future under this Lease.
        </p>
    </li>
    <li>
        <div class="raw-html-embed">
                        
            <div style="padding: 0.3rem; border: 2px solid gray;">
                                <strong>
                                <u>THEFT WARNING</u>
                                Lessee expressly acknowledges that failure to surrender the Equipment to Lessor after default or termination of this Lease may be prosecuted under Texas Penal Code Chapter 31 – Theft as a criminal offense which can result in Lessee’s arrest, indictment, conviction, and sentence by confinement in jail or prison plus a fine.
                                </strong>
                            
            </div>
                    
        </div>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Option to Buy Equipment</u>&nbsp;So long as Lessee has timely paid all rent and other sums due under this Lease and has duly performed all the covenants and obligations in this Lease, Lessee shall have the option to buy the Equipment on the Termination Date at the price stated on <u>Exhibit A</u> by delivering a written notice to Lessor at least sixty (60) days prior to the purchase.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Attorney’s Fees</u>&nbsp;If a Party defaults under this Lease and the other Party places this Lease with an attorney for enforcement, the defaulting Party shall pay to the enforcing Party the costs of such action, including reasonable attorney’s fees, whether or not a lawsuit is actually filed.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Construction and Captions</u>&nbsp;The paragraph captions in this Lease are only for reading convenience and do not constitute substantive matter to be considered in construing this Lease. The language of this Lease shall be construed and applied neutrally to both Parties, and shall not be construed or applied more strictly against the Party responsible for drafting, modifying, or finalizing the language of a Lease provision.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Severability</u>&nbsp;If any provision of this Lease (or the application of any provision to a specific person or circumstance) shall be held invalid or unenforceable for any reason, the remainder of this Lease (or the application of such provision to other persons or circumstances) shall not be deemed affected and shall be enforced to the greatest extent permitted by law.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>No Waiver</u>&nbsp;Lessor’s failure to complain for however long of any material default by Lessee shall not be deemed a waiver of any rights under this Lease. Lessor’s failure to declare a material default after its occurrence or failure to pursue any remedy against such default shall not be deemed to waive the default or the remedy, so that Lessor may at any subsequent time declare the default and/or pursue any remedy permitted under this Lease against such default. No waiver by Lessor of a provision of this Lease shall be construed as a waiver of any other provision, and a waiver of any provision shall not be construed as a waiver at a subsequent time of the same provision.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Notices</u>&nbsp;All notices, approvals, and communications in this Lease must be in writing and shall be deemed delivered (whether or not actually received or read) when: (a)&nbsp;delivered in person; (b)&nbsp;sent via internet to the recipient’s email address listed above; or (c)&nbsp;sent by U.S. First Class mail, postage prepaid, addressed to the address listed above for the intended recipient or at such other address as said intended recipient may specify from time to time by written notice.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>No Other Agreements</u>&nbsp;This Lease (with <u>Exhibit A)</u> constitutes the entire agreement of the Parties about the Equipment. There are no other oral or written representations, warranties, understandings, agreements, or promises between the Parties about this Lease or the Equipment. This Lease may be amended only by an instrument signed by both Lessor and Lessee.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Mediation</u>&nbsp;Any dispute of the Parties which is not resolved through informal discussion will be submitted to a mutually acceptable mediation service or provider. The Parties shall bear the mediation costs equally. This paragraph does not preclude a Party from seeking equitable relief from a court of competent jurisdiction.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Multiple Originals</u>&nbsp;This Lease may be executed in two or more counterparts, each of which will be deemed an original and all of which together will constitute one agreement. This Lease may be executed by actual, digital, or electronic signatures as permitted by law.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Governing Law and Venue</u>&nbsp;This Lease shall be read and interpreted according the laws of the State of Texas. The Parties expressly agree that exclusive jurisdiction and venue for any judicial action related to this Lease and/or the Equipment shall lie in Harris County, Texas.
        </p>
    </li>
    <li>
        <p style="text-align:justify;">
            <u>Time of Essence</u>&nbsp;Time is of the essence in the performance of this Lease.
        </p>
    </li>
</ol>
<div class="page-break" style="page-break-after:always;">
    <span style="display:none;">&nbsp;</span>
</div>
<p style="text-align:justify;">
    @@signatures_and_date_v2@@
</p>
<div class="page-break" style="page-break-after:always;">
    <span style="display:none;">&nbsp;</span>
</div>
<figure class="table">
    <table>
        <tbody>
            <tr>
                <td style="border:2px solid hsl(0, 0%, 30%);">
                    <p>
                        <span class="text-huge"><span lang="es-US" dir="ltr"><strong>G</strong></span></span><span lang="es-US" dir="ltr"> <u>Check and</u> sign <u>below only if applicable (chequee y firme al pié si se aplica lo siguiente):</u></span>
                    </p>
                    <p style="margin-left:40px;">
                        <span lang="es-US" dir="ltr">El Arrendatario (Lessee) certifica que:</span>
                    </p>
                    <ol style="list-style-type:lower-latin;">
                        <li>
                            <p style="margin-left:40px;">
                                <span lang="es-US" dir="ltr">un intérprete de su propia selección y de su confianza le tradujo este contrato del inglés al español;</span>
                            </p>
                        </li>
                        <li>
                            <p style="margin-left:40px;">
                                <span lang="es-US" dir="ltr">entiende plenamente el contenido de este contrato;</span>
                            </p>
                        </li>
                        <li>
                            <p style="margin-left:40px;">
                                <span lang="es-US" dir="ltr">ha tenido amplia oportunidad de consultar con su propio abogado o consejero sobre el significado y las consecuencias legales de este contrato; y</span>
                            </p>
                        </li>
                        <li>
                            <p style="margin-left:40px;">
                                <span lang="es-US" dir="ltr">firma este contrato por su libre albedrío y con conocimiento de su efecto.</span>
                            </p>
                        </li>
                    </ol>
                    <p style="margin-left:1in;text-align:center;">
                        <u>@@lessee_signature@@</u>
                    </p>
                    <p style="margin-left:1in;text-align:center;">
                        Arrendatario (Lessee)
                    </p>
                </td>
            </tr>
        </tbody>
    </table>
</figure>
"""


temp = TemplateVersion.objects.filter(
    module="rent",
    template="lease-conditions-rent",
    language="english",
    tmp_type="text",
).last()
temp.new_version(content=TemplRentV2)
