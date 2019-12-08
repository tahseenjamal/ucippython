package com.mtn.lib;

import java.io.File;
//import java.io.FileOutputStream;
//import java.io.IOException;
//import java.io.OutputStreamWriter;
//import java.io.PrintStream;
import java.io.StringWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Iterator;
import java.util.Scanner;

import javax.swing.JTextArea;
import javax.xml.namespace.QName;
import javax.xml.soap.MessageFactory;
//import javax.xml.soap.Node;
import javax.xml.soap.SOAPBody;
import javax.xml.soap.SOAPBodyElement;
import javax.xml.soap.SOAPConnection;
import javax.xml.soap.SOAPConnectionFactory;
import javax.xml.soap.SOAPElement;
import javax.xml.soap.SOAPEnvelope;
import javax.xml.soap.SOAPException;
import javax.xml.soap.SOAPHeader;
import javax.xml.soap.SOAPMessage;
import javax.xml.soap.SOAPPart;
import javax.xml.transform.OutputKeys;
//import javax.xml.transform.Result;
//import javax.xml.transform.Source;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import javax.xml.ws.soap.SOAPFaultException;

import org.w3c.dom.Document;
//import org.w3c.dom.NodeList;

//import com.mtn.ui.HssMainFrame;
//import com.mtn.ui.TextAreaOutputStream;

public class HssClient {

	private String sessionId;
	private String url;
	private String urlLogin;
	private SOAPConnection soapConnection;
	//private Result result;
	private JTextArea logWindow;

	public HssClient(String url ) {
		this.url = url;
		this.urlLogin = "http://10.195.5.7:8998/cai3g1_2/SessionControl/?wsdl";
		//this.result = new StreamResult(new File("C:\\temp\\result__.txt"));
		//this.logWindow = mainFrame.getLogArea();
		

	}

	private String convertToString (SOAPBody message) throws Exception{
		   Document doc = message.extractContentAsDocument();
		   StringWriter sw = new StringWriter();
		   TransformerFactory tf = TransformerFactory.newInstance();
		   Transformer transformer = tf.newTransformer();
		   transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, "no");
		   transformer.setOutputProperty(OutputKeys.METHOD, "xml");
		   transformer.setOutputProperty(OutputKeys.INDENT, "yes");
		   transformer.setOutputProperty(OutputKeys.ENCODING, "UTF-8");
		   transformer.transform(new DOMSource(doc), new StreamResult(sw));
		   return sw.toString();
    }
	public String getSessionId() {
		try {
			SOAPMessage res = callLogin("emamtngb", "EmaMtnBiss@u19");
			res.writeTo(System.out);
			SOAPBody body = res.getSOAPBody();
			System.out.println(body);
			//Iterator<SOAPElement> iter = body.getChildElements();
			Iterator<?> iter = body.getChildElements();
			String sessionId = null;
			while (iter.hasNext()) {
				SOAPElement el = (SOAPElement) iter.next();
				Iterator<?> innerIter = el.getChildElements();
				//Iterator<SOAPElement> innerIter = el.getChildElements();
				while (innerIter.hasNext()) {
					SOAPElement innerEl = (SOAPElement) innerIter.next();
					String tagName = innerEl.getLocalName();
					System.out.println(tagName);
					if (tagName.equals("sessionId")) {
						sessionId = innerEl.getValue();
						return sessionId;
					}
					// System.out.println("Session: " + innerEl.getLocalName());
					// System.out.println("Session: " + innerEl.getValue());
				}
				// break;
			}
		} catch (Exception ex) {
			System.out.println("Exception: " + ex.getMessage());
		}
		// System.out.println();
		System.out.println("Rufin: " + sessionId);
		return sessionId;
	}

	public void connect() {
		try {
			// Create SOAP Connection
			SOAPConnectionFactory soapConnectionFactory = SOAPConnectionFactory.newInstance();
			if (soapConnection == null)
				soapConnection = soapConnectionFactory.createConnection();
		} catch (Exception e) {
			System.err.println("Error occurred while sending SOAP Request to Server");
			e.printStackTrace();
		}
		this.sessionId = this.getSessionId();
		
	}

	public void close() throws Exception {
		if (soapConnection != null)
			soapConnection.close();
	}

	public boolean callGet(String msisdn, String imsi) throws Exception {
		//boolean success = true;
		SOAPMessage getMessage = this.createSOAPMessageGet(msisdn, imsi);
		//TransformerFactory transformerFactory = TransformerFactory.newInstance();
		//Transformer transformer = transformerFactory.newTransformer();

		SOAPMessage soapResponse = soapConnection.call(getMessage, this.url);
		
		SOAPBody body = soapResponse.getSOAPBody();
		String xml = this.convertToString(body);
		
		Date dateObject = new Date();
		SimpleDateFormat dateFormatter = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss");
		String date = dateFormatter.format(dateObject);
		
		this.logWindow.append("\n============="+  date + "==============\n" + xml );
		this.logWindow.setCaretPosition(this.logWindow.getText().length());
		if (xml.indexOf("No such object") != -1 || xml.indexOf("faultcode") != -1 )
			return false;
		return true;
//		org.w3c.dom.Node msisdnNode =  body.getElementsByTagName("msisdn").item(0);
//		org.w3c.dom.Node  imsiNode =  body.getElementsByTagName("imsi").item(0);
//		
//		if (msisdnNode == null || imsiNode == null)
//			return null;
//		System.out.println("====== " + msisdnNode.getTextContent() + " ===== " +  imsiNode.getTextContent());
//		return new EmaUser(msisdnNode.getTextContent(), imsiNode.getTextContent());
		
	}

	private SOAPMessage callLogin(String user, String pass) throws Exception {

		SOAPMessage loginMessage = this.createSOAPMessageLogin(user, pass);
		//TransformerFactory transformerFactory = TransformerFactory.newInstance();
		//Transformer transformer = transformerFactory.newTransformer();

		SOAPMessage soapResponse = soapConnection.call(loginMessage, this.urlLogin);

		//Source sourceContent = soapResponse.getSOAPPart().getContent();

		// fos.write(sourceContent.toString().getBytes());

		//System.out.println("\nResponse SOAP Message = ");
		//StreamResult result = new StreamResult(System.out);
		//transformer.transform(sourceContent, result);

		return soapResponse;
	}

	public boolean callDelete(String msisdn, String imsi) throws Exception {

		SOAPMessage deleteMessage = this.createSOAPMessageDelete(msisdn, imsi);
		//TransformerFactory transformerFactory = TransformerFactory.newInstance();
		//Transformer transformer = transformerFactory.newTransformer();

		SOAPMessage soapResponse = soapConnection.call(deleteMessage, this.url);
		SOAPBody body = soapResponse.getSOAPBody();
		
		String xml = this.convertToString(body);
		//
		
		Date dateObject = new Date();
		SimpleDateFormat dateFormatter = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss");
		String date = dateFormatter.format(dateObject);
		
		this.logWindow.append("\n============="+  date + "==============\n" + xml );
		this.logWindow.setCaretPosition(this.logWindow.getText().length());
		if (xml.indexOf("No such object") != -1 || xml.indexOf("faultcode") != -1 )
			return false;
		return true;

//		Source sourceContent = soapResponse.getSOAPPart().getContent();
//
//		System.out.println("\nResponse SOAP Message = ");
//		StreamResult result = new StreamResult(System.out);
//		transformer.transform(sourceContent, result);
//		return success;

	}

	public boolean callCreate(String msisdn, String imsi, String profileId) throws SOAPException, SOAPFaultException, Exception {

		boolean success = true;
		SOAPMessage createMessage = this.createSOAPMessageCreate(msisdn, imsi, profileId);
		//TransformerFactory transformerFactory = TransformerFactory.newInstance();
		//Transformer transformer = transformerFactory.newTransformer();

		SOAPMessage soapResponse = soapConnection.call(createMessage, this.url);

		SOAPBody body = soapResponse.getSOAPBody();

		String xml = this.convertToString(body);
		
		//Date dateObject = new Date();
		//SimpleDateFormat dateFormatter = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss");
		//String date = dateFormatter.format(dateObject);
		
		// Begin new
//		System.out.println("************************************** coco **************************");
//		if (soapResponse.getSOAPBody().hasFault()){
//			//soapResponse.getSOAPBody().getFault();
//			this.logWindow.append("\n============="+  date + "==============\n" + soapResponse.getSOAPBody().getFault().toString() );
//			System.out.println("////////////////////////////////////////////////////////////////////////////////////////Aqui");
//			//this.logWindow.setCaretPosition(this.logWindow.getText().length());
//			return false;
//			
//		}
		
		/// End new
		
		//this.logWindow.append("\n============="+  date + "==============\n" + xml );
		//this.logWindow.setCaretPosition(this.logWindow.getText().length());
		//System.out.println(xml);
		if (xml.indexOf("CONSTRAINT VIOLATION") != -1 || xml.indexOf("faultcode") != -1 )
			success = false;
		return success;

	}

	private SOAPMessage createSOAPMessageDelete(String msisdn, String imsi) throws Exception {
		MessageFactory factory = MessageFactory.newInstance();
		SOAPMessage message = factory.createMessage();

		SOAPPart soapPart = message.getSOAPPart();
		SOAPEnvelope envelope = soapPart.getEnvelope();
		SOAPHeader header = envelope.getHeader();
		SOAPBody body = envelope.getBody();

		// Additionnal namespace on envelope
		envelope.addNamespaceDeclaration("SOAP-ENC", "http://schemas.xmlsoap.org/soap/encoding/");
		envelope.addNamespaceDeclaration("xsi", "http://www.w3.org/2001/XMLSchema-instance");
		envelope.addNamespaceDeclaration("xsd", "http://www.w3.org/2001/XMLSchema");
		envelope.addNamespaceDeclaration("cai3g", "http://schemas.ericsson.com/cai3g1.2/");
		envelope.addNamespaceDeclaration("sim", "http://schemas.ericsson.com/ema/UserProvisioning/Ecms/SIM/");

		// Add Header
		SOAPElement sequence = header.addChildElement("SequenceId", "cai3g");
		sequence.addTextNode("193796089649584960");
		SOAPElement trnx = header.addChildElement("TransactionId", "cai3g");
		trnx.addTextNode("0000000");
		SOAPElement session = header.addChildElement("SessionId", "cai3g");

		String sessionId = this.sessionId;//this.getSessionId();
		session.addTextNode(sessionId);

		// Add Body
		QName bodyName = new QName("http://schemas.ericsson.com/cai3g1.2/", "Delete", "cai3g");
		SOAPBodyElement bodyElement = body.addBodyElement(bodyName);

		SOAPElement motype = bodyElement.addChildElement("MOType", "cai3g");
		motype.addTextNode("EPSMultiSC@http://schemas.ericsson.com/ma/HSS/");

		SOAPElement moid = bodyElement.addChildElement("MOId", "cai3g");
		SOAPElement momsisdn = moid.addChildElement("msisdn");
		momsisdn.addTextNode(msisdn);

		SOAPElement moatt = bodyElement.addChildElement("MOAttributes", "cai3g");
		SOAPElement delM = moatt.addChildElement("DeleteEPSMultiSC");
		SOAPElement s_imsi = delM.addChildElement("imsi");
		s_imsi.addTextNode(imsi);
		SOAPElement subscr = delM.addChildElement("subscriptionId");
		subscr.addTextNode(msisdn);

		System.out.println("--------------- REQUEST ------------");
		message.writeTo(System.out);
		System.out.println();
		return message;
	}

	private SOAPMessage createSOAPMessageCreate(String msisdn, String imsi, String profile) throws Exception {
		MessageFactory factory = MessageFactory.newInstance();
		SOAPMessage message = factory.createMessage();

		SOAPPart soapPart = message.getSOAPPart();
		SOAPEnvelope envelope = soapPart.getEnvelope();
		SOAPHeader header = envelope.getHeader();
		SOAPBody body = envelope.getBody();

		// Additionnal namespace on envelope
		envelope.addNamespaceDeclaration("SOAP-ENC", "http://schemas.xmlsoap.org/soap/encoding/");
		envelope.addNamespaceDeclaration("xsi", "http://www.w3.org/2001/XMLSchema-instance");
		envelope.addNamespaceDeclaration("xsd", "http://www.w3.org/2001/XMLSchema");
		envelope.addNamespaceDeclaration("cai3g", "http://schemas.ericsson.com/cai3g1.2/");
		envelope.addNamespaceDeclaration("sim", "http://schemas.ericsson.com/ema/UserProvisioning/Ecms/SIM/");

		// Add Header
		SOAPElement sequence = header.addChildElement("SequenceId", "cai3g");
		sequence.addTextNode("193796089649584960");
		SOAPElement trnx = header.addChildElement("TransactionId", "cai3g");
		trnx.addTextNode("0000000");
		SOAPElement session = header.addChildElement("SessionId", "cai3g");

		String sessionId = this.sessionId;
		session.addTextNode(sessionId);

		// Add Body
		QName bodyName = new QName("http://schemas.ericsson.com/cai3g1.2/", "Create", "cai3g");
		SOAPBodyElement bodyElement = body.addBodyElement(bodyName);

		SOAPElement motype = bodyElement.addChildElement("MOType", "cai3g");
		motype.addTextNode("EPSMultiSC@http://schemas.ericsson.com/ma/HSS/");

		SOAPElement moid = bodyElement.addChildElement("MOId", "cai3g");
		SOAPElement momsisdn = moid.addChildElement("msisdn");
		momsisdn.addTextNode(msisdn);

		SOAPElement moatt = bodyElement.addChildElement("MOAttributes", "cai3g");
		SOAPElement delM = moatt.addChildElement("CreateEPSMultiSC");

		delM.addAttribute(envelope.createName("imsi"), imsi);

		SOAPElement s_imsi = delM.addChildElement("imsi");
		s_imsi.addTextNode(imsi);

		SOAPElement m_msisdn = delM.addChildElement("msisdn");
		m_msisdn.addTextNode(msisdn);

		SOAPElement subscr = delM.addChildElement("subscriptionId");
		subscr.addTextNode(msisdn);

		SOAPElement m_profileId = delM.addChildElement("epsProfileId");
		m_profileId.addTextNode(profile);
		
		// ROAMING attributes
		SOAPElement roamingAllowed = delM.addChildElement("epsRoamingAllowed");
		roamingAllowed.addTextNode("TRUE");
		SOAPElement roamingRestriction  = delM.addChildElement("epsRoamingRestriction");
		roamingRestriction.addTextNode("FALSE");
		
		System.out.println("--------------- REQUEST ------------");
		message.writeTo(System.out);
		System.out.println();
		return message;
	}

	private SOAPMessage createSOAPMessageLogin(String username, String password) throws Exception {
		MessageFactory factory = MessageFactory.newInstance();
		SOAPMessage message = factory.createMessage();

		SOAPPart soapPart = message.getSOAPPart();
		SOAPEnvelope envelope = soapPart.getEnvelope();
		//SOAPHeader header = envelope.getHeader();
		SOAPBody body = envelope.getBody();

		envelope.addNamespaceDeclaration("cai3g", "http://schemas.ericsson.com/cai3g1.2/");

		SOAPElement login = body.addChildElement("Login", "cai3g");
		SOAPElement user = login.addChildElement("userId", "cai3g");
		user.addTextNode(username);

		SOAPElement pass = login.addChildElement("pwd", "cai3g");
		pass.addTextNode(password);

		System.out.println("--------------- REQUEST ------------");
		message.writeTo(System.out);
		System.out.println();
		return message;
	}

	private SOAPMessage createSOAPMessageGet(String msisdn, String imsi) throws Exception {
		MessageFactory factory = MessageFactory.newInstance();
		SOAPMessage message = factory.createMessage();

		SOAPPart soapPart = message.getSOAPPart();
		SOAPEnvelope envelope = soapPart.getEnvelope();
		SOAPHeader header = envelope.getHeader();
		SOAPBody body = envelope.getBody();

		// Additionnal namespace on envelope
		envelope.addNamespaceDeclaration("SOAP-ENC", "http://schemas.xmlsoap.org/soap/encoding/");
		envelope.addNamespaceDeclaration("xsi", "http://www.w3.org/2001/XMLSchema-instance");
		envelope.addNamespaceDeclaration("xsd", "http://www.w3.org/2001/XMLSchema");
		envelope.addNamespaceDeclaration("cai3g", "http://schemas.ericsson.com/cai3g1.2/");
		envelope.addNamespaceDeclaration("sim", "http://schemas.ericsson.com/ema/UserProvisioning/Ecms/SIM/");

		// Add Header
		SOAPElement sequence = header.addChildElement("SequenceId", "cai3g");
		sequence.addTextNode("193796089649584960");
		SOAPElement trnx = header.addChildElement("TransactionId", "cai3g");
		trnx.addTextNode("0000000");
		SOAPElement session = header.addChildElement("SessionId", "cai3g");
		String sessionId = this.getSessionId();
		session.addTextNode(sessionId);

		// new QName("http://lit.com/schemas/Bobsled", "bob:sessionId","bob")
		// <bob:sessionId xmlns:bob="http://lit.com/schemas/Bobsled">
		// Add Body
		QName bodyName = new QName("http://schemas.ericsson.com/cai3g1.2/", "Get", "cai3g");

		SOAPBodyElement bodyElement = body.addBodyElement(bodyName);
		// body.addch

		// bodyElement.addAttribute(new
		// QName("http://schemas.ericsson.com/cai3g1.2/"), "cai3g");

		SOAPElement motype = bodyElement.addChildElement("MOType", "cai3g");
		motype.addTextNode("EPSMultiSC@http://schemas.ericsson.com/ma/HSS/");

		SOAPElement moid = bodyElement.addChildElement("MOId", "cai3g");
		SOAPElement momsisdn = moid.addChildElement("msisdn");
		momsisdn.addTextNode(msisdn);

		SOAPElement moatt = bodyElement.addChildElement("MOAttributes", "cai3g");
		SOAPElement delM = moatt.addChildElement("GetEPSMultiSC");
		SOAPElement s_imsi = delM.addChildElement("imsi");
		s_imsi.addTextNode(imsi);
		SOAPElement subscr = delM.addChildElement("subscriptionId");
		subscr.addTextNode(msisdn);

		System.out.println("\n--------------- REQUEST ------------");
		message.writeTo(System.out);
		System.out.println();
		return message;
	}

	public static void main(String[] args) throws Exception {

		// TODO Auto-generated method stub
		// String line;
		// 245966601471,632020104173257

		// TODO Auto-generated method stub
		 String line;
		 String tokens[];
		 try {
			 Scanner scan = new Scanner(new File("/home/everaldo/numbers"));
			 HssClient cli = new HssClient("http://10.195.5.7:8998/cai3g1_2/Provisioning/?wsdl");
			 cli.connect();
			 // //System.out.println(" --- "+ cli.getSessionId());
			 while (scan.hasNext()) {
				 line = scan.nextLine();
				 System.out.println(line);
				 tokens = line.split(",");
				 //cli.callDelete(tokens[0], tokens[1]
				 //cli.callCreate(tokens[0], tokens[1], "2"
				 if (cli.callCreate(tokens[0], tokens[1], tokens[2])){
					 //System.out.println("\r\n" + tokens[0] + "---> Success"); line
					System.out.println(line + " ---> Success");
				 }
				 else{
					 System.out.println("\r\n" + tokens[0] + "---> Error. User does not exits.");
				 }
			 }
			 scan.close();
			 cli.close();
		}
		
		catch (Exception e) {
			 e.printStackTrace();
		 }
	}
}
